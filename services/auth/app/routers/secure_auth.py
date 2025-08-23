from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from ..security.middleware import (
    get_current_user, 
    get_optional_user, 
    require_admin,
    require_authenticated
)
from ..security.advanced_rate_limit import rate_limiter, check_auth_rate_limit
from ..security.session_manager import session_manager
from ..validation.validators import (
    SecureEmailRegisterRequest,
    SecureEmailLoginRequest,
    EmailVerifyRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    RefreshTokenRequest,
    validate_user_agent,
    validate_ip_address
)
from ..services import email_flows
try:
    from ..db.database import get_db
except ImportError:
    # Fallback to the existing database setup
    from ..routers.email import get_db

router = APIRouter(prefix="/api/auth", dependencies=[Depends(check_auth_rate_limit)])


def get_client_info(request: Request, user_agent: str = Header(None)) -> Dict[str, Any]:
    """Extract client information from request."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Validate IP address
    if not validate_ip_address(client_ip):
        client_ip = "unknown"
    
    # Sanitize user agent
    sanitized_ua = validate_user_agent(user_agent)
    
    return {
        "ip_address": client_ip,
        "user_agent": sanitized_ua
    }


@router.post("/email/register")
async def secure_register(
    request: Request,
    req: SecureEmailRegisterRequest, 
    db: Session = Depends(get_db),
    user_agent: str = Header(None)
):
    """Secure email registration with enhanced validation."""
    client_info = get_client_info(request, user_agent)
    client_ip = client_info["ip_address"]
    
    try:
        # Check rate limits for registration
        if not rate_limiter.check_login_attempts(f"register:{req.email}", max_attempts=3):
            raise HTTPException(status_code=429, detail="Too many registration attempts for this email")
        
        if not rate_limiter.check_login_attempts(f"register_ip:{client_ip}", max_attempts=5):
            raise HTTPException(status_code=429, detail="Too many registration attempts from this IP")
        
        # Register user
        token = email_flows.register(db, req.email, req.password)
        
        # Clear failed attempts on success
        rate_limiter.clear_attempts(f"register:{req.email}")
        
        return {
            "message": "Registration successful. Please check your email for verification.",
            "email": req.email
        }
        
    except HTTPException as e:
        # Record failed attempt
        rate_limiter.record_failed_attempt(f"register:{req.email}")
        rate_limiter.record_failed_attempt(f"register_ip:{client_ip}")
        raise e
    except Exception as e:
        # Record failed attempt for unexpected errors
        rate_limiter.record_failed_attempt(f"register:{req.email}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/email/verify")
async def secure_verify(
    request: Request,
    req: EmailVerifyRequest,
    db: Session = Depends(get_db),
    user_agent: str = Header(None)
):
    """Secure email verification."""
    client_info = get_client_info(request, user_agent)
    
    try:
        # Verify email and get tokens
        result = email_flows.verify(db, req.token)
        
        # Create session
        device_info = {"user_agent": client_info["user_agent"]}
        session_id = session_manager.create_session(
            result.get("user_id", "unknown"), 
            device_info, 
            client_info["ip_address"]
        )
        
        return {
            **result,
            "session_id": session_id,
            "message": "Email verified successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Email verification failed")


@router.post("/login")
async def secure_login(
    request: Request,
    req: SecureEmailLoginRequest,
    db: Session = Depends(get_db),
    user_agent: str = Header(None)
):
    """Secure login with session management."""
    client_info = get_client_info(request, user_agent)
    client_ip = client_info["ip_address"]
    
    try:
        # Check rate limits
        if not rate_limiter.check_login_attempts(f"login:{req.email}", max_attempts=5):
            raise HTTPException(status_code=429, detail="Too many login attempts for this email")
        
        if not rate_limiter.check_login_attempts(f"login_ip:{client_ip}", max_attempts=10):
            raise HTTPException(status_code=429, detail="Too many login attempts from this IP")
        
        # Authenticate user
        result = email_flows.login(db, req.email, req.password, req.remember_me)
        
        # Create session
        device_info = req.device_info or {}
        device_info.update({"user_agent": client_info["user_agent"]})
        
        session_id = session_manager.create_session(
            result.get("user_id", "unknown"),
            device_info,
            client_ip
        )
        
        # Clear failed attempts on successful login
        rate_limiter.clear_attempts(f"login:{req.email}")
        rate_limiter.clear_attempts(f"login_ip:{client_ip}")
        
        return {
            **result,
            "session_id": session_id,
            "message": "Login successful"
        }
        
    except HTTPException as e:
        # Record failed attempt
        rate_limiter.record_failed_attempt(f"login:{req.email}")
        rate_limiter.record_failed_attempt(f"login_ip:{client_ip}")
        raise e
    except Exception as e:
        # Record failed attempt for unexpected errors
        rate_limiter.record_failed_attempt(f"login:{req.email}")
        rate_limiter.record_failed_attempt(f"login_ip:{client_ip}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout")
async def logout(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Secure logout with session cleanup."""
    try:
        session_manager.revoke_session(session_id)
        return {"message": "Logged out successfully"}
    except Exception:
        # Even if session cleanup fails, return success
        return {"message": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all(current_user: dict = Depends(get_current_user)):
    """Logout from all devices."""
    try:
        session_manager.revoke_all_user_sessions(current_user["user_id"])
        return {"message": "Logged out from all devices successfully"}
    except Exception:
        return {"message": "Logged out from all devices successfully"}


@router.get("/sessions")
async def get_user_sessions(current_user: dict = Depends(get_current_user)):
    """Get all active sessions for the current user."""
    try:
        sessions = session_manager.get_user_sessions(current_user["user_id"])
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Revoke a specific session."""
    try:
        # Verify the session belongs to the current user
        sessions = session_manager.get_user_sessions(current_user["user_id"])
        session_exists = any(s["session_id"] == session_id for s in sessions)
        
        if not session_exists:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_manager.revoke_session(session_id)
        return {"message": "Session revoked successfully"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to revoke session")


@router.post("/password/reset/request")
async def password_reset_request(
    request: Request,
    req: PasswordResetRequest,
    db: Session = Depends(get_db),
    user_agent: str = Header(None)
):
    """Request password reset with rate limiting."""
    client_info = get_client_info(request, user_agent)
    client_ip = client_info["ip_address"]
    
    try:
        # Check rate limits
        if not rate_limiter.check_login_attempts(f"reset:{req.email}", max_attempts=3):
            raise HTTPException(status_code=429, detail="Too many reset requests for this email")
        
        if not rate_limiter.check_login_attempts(f"reset_ip:{client_ip}", max_attempts=5):
            raise HTTPException(status_code=429, detail="Too many reset requests from this IP")
        
        # Request password reset
        email_flows.request_password_reset(db, req.email)
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception:
        # Record failed attempt but still return success message
        rate_limiter.record_failed_attempt(f"reset:{req.email}")
        rate_limiter.record_failed_attempt(f"reset_ip:{client_ip}")
        return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password/reset/confirm")
async def password_reset_confirm(
    request: Request,
    req: PasswordResetConfirmRequest,
    db: Session = Depends(get_db),
    user_agent: str = Header(None)
):
    """Confirm password reset."""
    client_info = get_client_info(request, user_agent)
    
    try:
        # Confirm password reset
        email_flows.confirm_password_reset(db, req.token, req.new_password)
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Password reset failed")


@router.post("/refresh")
async def refresh_token(
    request: Request,
    req: RefreshTokenRequest,
    db: Session = Depends(get_db),
    user_agent: str = Header(None)
):
    """Refresh access token."""
    client_info = get_client_info(request, user_agent)
    
    try:
        # This would need to be implemented in email_flows
        # For now, return an error
        raise HTTPException(status_code=501, detail="Token refresh not yet implemented")
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.get("/profile")
async def get_profile(current_user: dict = Depends(require_authenticated)):
    """Get current user profile (protected endpoint)."""
    return {
        "user_id": current_user["user_id"],
        "roles": current_user["roles"],
        "message": "Profile retrieved successfully"
    }


@router.get("/admin/users")
async def admin_get_users(current_user: dict = Depends(require_admin)):
    """Admin endpoint to get users (example of role-based access)."""
    # This would typically fetch users from database
    return {
        "message": "Admin access granted",
        "admin_user": current_user["user_id"]
    }


@router.get("/health")
async def health_check():
    """Health check endpoint (no authentication required)."""
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": "2024-01-01T00:00:00Z"  # In real implementation, use actual timestamp
    }
