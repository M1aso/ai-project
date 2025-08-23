import os
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
import redis


class SessionManager:
    """Secure session management with Redis backend."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_password = os.getenv("REDIS_PASSWORD")
        
        if redis_client:
            self.redis = redis_client
        else:
            try:
                self.redis = redis.Redis(
                    host=redis_host, 
                    port=redis_port, 
                    password=redis_password,
                    db=1,  # Use different database for sessions
                    decode_responses=True
                )
                # Test connection
                self.redis.ping()
            except (redis.RedisError, redis.ConnectionError):
                # Fallback to in-memory storage if Redis is not available
                self.redis = None
                self._memory_store = {}
    
    def _cleanup_memory_store(self):
        """Clean up expired sessions from memory store."""
        if self.redis:
            return
        
        now = datetime.now(timezone.utc)
        expired_keys = []
        
        for key, data in self._memory_store.items():
            if '_expires' in data:
                try:
                    expires_at = datetime.fromisoformat(data['_expires'])
                    if now > expires_at:
                        expired_keys.append(key)
                except ValueError:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._memory_store[key]
    
    def create_session(self, user_id: str, device_info: Dict, ip_address: str) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "device_info": device_info,
            "ip_address": ip_address,
            "is_active": True
        }
        
        session_ttl = int(os.getenv("SESSION_TTL", 30 * 24 * 3600))  # 30 days
        
        if self.redis:
            try:
                # Store session
                self.redis.setex(f"session:{session_id}", session_ttl, json.dumps(session_data))
                
                # Track user sessions
                user_sessions_key = f"user_sessions:{user_id}"
                self.redis.sadd(user_sessions_key, session_id)
                self.redis.expire(user_sessions_key, session_ttl)
            except redis.RedisError:
                pass
        else:
            # Memory store fallback
            self._cleanup_memory_store()
            session_data['_expires'] = (datetime.now(timezone.utc) + timedelta(seconds=session_ttl)).isoformat()
            self._memory_store[f"session:{session_id}"] = session_data
            
            # Track user sessions in memory
            user_sessions_key = f"user_sessions:{user_id}"
            if user_sessions_key not in self._memory_store:
                self._memory_store[user_sessions_key] = {
                    "sessions": [],
                    "_expires": (datetime.now(timezone.utc) + timedelta(seconds=session_ttl)).isoformat()
                }
            self._memory_store[user_sessions_key]["sessions"].append(session_id)
        
        return session_id
    
    def validate_session(self, session_id: str, ip_address: str) -> Optional[Dict]:
        """Validate session and update last activity."""
        session_key = f"session:{session_id}"
        
        try:
            if self.redis:
                data = self.redis.get(session_key)
                if not data:
                    return None
                session_data = json.loads(data)
            else:
                self._cleanup_memory_store()
                session_data = self._memory_store.get(session_key)
                if not session_data:
                    return None
                
                # Check expiration for memory store
                if '_expires' in session_data:
                    expires_at = datetime.fromisoformat(session_data['_expires'])
                    if datetime.now(timezone.utc) > expires_at:
                        del self._memory_store[session_key]
                        return None
            
            # Check if session is active
            if not session_data.get("is_active"):
                return None
            
            # Optional: Check IP consistency (can be disabled for mobile users)
            stored_ip = session_data.get("ip_address")
            if stored_ip and stored_ip != ip_address:
                # Log potential session hijacking but don't block
                # In production, you might want to invalidate the session
                pass
            
            # Update last activity
            session_data["last_activity"] = datetime.now(timezone.utc).isoformat()
            
            session_ttl = int(os.getenv("SESSION_TTL", 30 * 24 * 3600))
            
            if self.redis:
                self.redis.setex(session_key, session_ttl, json.dumps(session_data))
            else:
                session_data['_expires'] = (datetime.now(timezone.utc) + timedelta(seconds=session_ttl)).isoformat()
                self._memory_store[session_key] = session_data
            
            return session_data
            
        except (json.JSONDecodeError, ValueError):
            return None
    
    def revoke_session(self, session_id: str):
        """Revoke a specific session."""
        session_key = f"session:{session_id}"
        
        try:
            if self.redis:
                data = self.redis.get(session_key)
                if data:
                    session_data = json.loads(data)
                    user_id = session_data.get("user_id")
                    
                    # Remove from user sessions
                    if user_id:
                        self.redis.srem(f"user_sessions:{user_id}", session_id)
                
                self.redis.delete(session_key)
            else:
                session_data = self._memory_store.get(session_key)
                if session_data:
                    user_id = session_data.get("user_id")
                    if user_id:
                        user_sessions_key = f"user_sessions:{user_id}"
                        user_sessions_data = self._memory_store.get(user_sessions_key, {})
                        sessions = user_sessions_data.get("sessions", [])
                        if session_id in sessions:
                            sessions.remove(session_id)
                            user_sessions_data["sessions"] = sessions
                            self._memory_store[user_sessions_key] = user_sessions_data
                
                self._memory_store.pop(session_key, None)
                
        except (json.JSONDecodeError, redis.RedisError):
            pass
    
    def revoke_all_user_sessions(self, user_id: str):
        """Revoke all sessions for a user."""
        user_sessions_key = f"user_sessions:{user_id}"
        
        try:
            if self.redis:
                sessions = self.redis.smembers(user_sessions_key)
                for session_id in sessions:
                    self.redis.delete(f"session:{session_id}")
                
                self.redis.delete(user_sessions_key)
            else:
                user_sessions_data = self._memory_store.get(user_sessions_key, {})
                sessions = user_sessions_data.get("sessions", [])
                
                for session_id in sessions:
                    self._memory_store.pop(f"session:{session_id}", None)
                
                self._memory_store.pop(user_sessions_key, None)
                
        except redis.RedisError:
            pass
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all active sessions for a user."""
        user_sessions_key = f"user_sessions:{user_id}"
        sessions = []
        
        try:
            if self.redis:
                session_ids = self.redis.smembers(user_sessions_key)
                for session_id in session_ids:
                    data = self.redis.get(f"session:{session_id}")
                    if data:
                        session_data = json.loads(data)
                        if session_data.get("is_active"):
                            sessions.append({
                                "session_id": session_id,
                                "created_at": session_data.get("created_at"),
                                "last_activity": session_data.get("last_activity"),
                                "device_info": session_data.get("device_info", {}),
                                "ip_address": session_data.get("ip_address")
                            })
            else:
                self._cleanup_memory_store()
                user_sessions_data = self._memory_store.get(user_sessions_key, {})
                session_ids = user_sessions_data.get("sessions", [])
                
                for session_id in session_ids:
                    session_data = self._memory_store.get(f"session:{session_id}")
                    if session_data and session_data.get("is_active"):
                        sessions.append({
                            "session_id": session_id,
                            "created_at": session_data.get("created_at"),
                            "last_activity": session_data.get("last_activity"),
                            "device_info": session_data.get("device_info", {}),
                            "ip_address": session_data.get("ip_address")
                        })
            
        except (json.JSONDecodeError, redis.RedisError):
            pass
        
        return sessions


# Global session manager instance
session_manager = SessionManager()
