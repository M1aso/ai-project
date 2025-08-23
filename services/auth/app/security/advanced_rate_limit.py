import os
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from fastapi import HTTPException, Request
import redis


class AdvancedRateLimiter:
    """Redis-backed rate limiter with progressive delays."""
    
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
                    db=0,
                    decode_responses=True
                )
                # Test connection
                self.redis.ping()
            except (redis.RedisError, redis.ConnectionError):
                # Fallback to in-memory storage if Redis is not available
                self.redis = None
                self._memory_store = {}
    
    def _get_key_data(self, key: str) -> dict:
        """Get data for a key from Redis or memory store."""
        if self.redis:
            try:
                data = self.redis.get(key)
                return json.loads(data) if data else {}
            except (redis.RedisError, json.JSONDecodeError):
                return {}
        else:
            return self._memory_store.get(key, {})
    
    def _set_key_data(self, key: str, data: dict, ttl: int = 86400):
        """Set data for a key in Redis or memory store."""
        if self.redis:
            try:
                self.redis.setex(key, ttl, json.dumps(data))
            except redis.RedisError:
                pass
        else:
            # Simple memory cleanup for keys older than TTL
            data['_expires'] = (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat()
            self._memory_store[key] = data
    
    def _delete_key(self, key: str):
        """Delete a key from Redis or memory store."""
        if self.redis:
            try:
                self.redis.delete(key)
            except redis.RedisError:
                pass
        else:
            self._memory_store.pop(key, None)
    
    def check_login_attempts(self, identifier: str, max_attempts: int = 5) -> bool:
        """Check login attempts with exponential backoff."""
        key = f"login_attempts:{identifier}"
        
        data = self._get_key_data(key)
        if not data:
            return True
        
        # Check memory store expiration
        if not self.redis and '_expires' in data:
            if datetime.now(timezone.utc) > datetime.fromisoformat(data['_expires']):
                self._delete_key(key)
                return True
        
        attempts = data.get("count", 0)
        last_attempt_str = data.get("last_attempt")
        
        if not last_attempt_str:
            return True
        
        try:
            last_attempt = datetime.fromisoformat(last_attempt_str)
        except ValueError:
            return True
        
        # Progressive delay: 1min, 5min, 15min, 1hour, 24hours
        delays = [60, 300, 900, 3600, 86400]
        if attempts >= max_attempts:
            delay_index = min(attempts - max_attempts, len(delays) - 1)
            required_delay = delays[delay_index]
            
            time_passed = (datetime.now(timezone.utc) - last_attempt).total_seconds()
            if time_passed < required_delay:
                remaining_minutes = int((required_delay - time_passed) / 60)
                raise HTTPException(
                    status_code=429, 
                    detail=f"Too many failed attempts. Try again in {remaining_minutes} minutes."
                )
            else:
                # Reset after delay period
                self._delete_key(key)
                return True
        
        return True
    
    def record_failed_attempt(self, identifier: str):
        """Record a failed login attempt."""
        key = f"login_attempts:{identifier}"
        
        data = self._get_key_data(key)
        count = data.get("count", 0) + 1
        
        new_data = {
            "count": count,
            "last_attempt": datetime.now(timezone.utc).isoformat()
        }
        
        # Expire after 24 hours
        self._set_key_data(key, new_data, 86400)
    
    def clear_attempts(self, identifier: str):
        """Clear failed attempts after successful login."""
        key = f"login_attempts:{identifier}"
        self._delete_key(key)
    
    def check_rate_limit(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """Generic rate limiting check."""
        key = f"rate_limit:{identifier}"
        
        now = datetime.now(timezone.utc)
        data = self._get_key_data(key)
        
        # Get request timestamps within the window
        requests = data.get("requests", [])
        window_start = now - timedelta(seconds=window_seconds)
        
        # Filter requests within the window
        recent_requests = []
        for req_time_str in requests:
            try:
                req_time = datetime.fromisoformat(req_time_str)
                if req_time > window_start:
                    recent_requests.append(req_time_str)
            except ValueError:
                continue
        
        if len(recent_requests) >= limit:
            return False
        
        # Add current request
        recent_requests.append(now.isoformat())
        
        # Store updated data
        self._set_key_data(key, {"requests": recent_requests}, window_seconds)
        
        return True


# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()


async def check_rate_limit(request: Request):
    """Middleware to check rate limits."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Skip rate limiting for health checks
    if request.url.path in ["/healthz", "/readyz", "/metrics"]:
        return
    
    # Check IP-based rate limiting (100 requests per hour)
    if not rate_limiter.check_rate_limit(f"ip:{client_ip}", limit=100, window_seconds=3600):
        raise HTTPException(status_code=429, detail="Too many requests from this IP")


async def check_auth_rate_limit(request: Request):
    """More strict rate limiting for authentication endpoints."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Check IP-based auth rate limiting (10 requests per hour)
    if not rate_limiter.check_rate_limit(f"auth_ip:{client_ip}", limit=10, window_seconds=3600):
        raise HTTPException(status_code=429, detail="Too many authentication attempts from this IP")
