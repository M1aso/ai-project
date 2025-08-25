from fastapi import APIRouter, Depends, Request, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone

from ..security.middleware import (
    get_current_user, 
    get_optional_user, 
    require_admin,
    require_authenticated
)
from ..db import models
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

# Security scheme for Swagger UI
security = HTTPBearer()

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    dependencies=[Depends(check_auth_rate_limit)],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"}
    }
)


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


@router.post(
    "/email/register",
    summary="Register new user",
    description="Register a new user account with email and password. Sends verification email.",
    response_description="Registration successful, verification email sent",
    tags=["Public Endpoints"],
    responses={
        200: {
            "description": "Registration successful",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Registration successful. Please check your email for verification.",
                        "email": "user@example.com"
                    }
                }
            }
        },
        400: {"description": "Email already registered or invalid input"},
        429: {"description": "Too many registration attempts"}
    }
)
async def secure_register(
    request: Request,
    req: SecureEmailRegisterRequest, 
    db: Session = Depends(get_db),
    user_agent: str = Header(None)
):
    """Register a new user account with email and password verification."""
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
    """Secure email verification via POST."""
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


@router.get(
    "/email/verify",
    summary="Verify email address (link)",
    description="Verify email address by clicking the link in verification email. Returns JWT tokens on success.",
    response_description="Email verified successfully, user activated",
    tags=["Public Endpoints"],
    responses={
        200: {
            "description": "Email verified successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
                        "session_id": "02c8e432-1500-4c16-b0ef-f65cf309ea48",
                        "message": "Email verified successfully! You can now log in."
                    }
                }
            }
        },
        400: {"description": "Invalid or expired verification token"}
    }
)
async def verify_email_link(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
    user_agent: str = Header(None)
):
    """Verify email address using the verification token from email link."""
    client_info = get_client_info(request, user_agent)
    
    try:
        # Verify email and get tokens
        result = email_flows.verify(db, token)
        
        # Create session
        device_info = {"user_agent": client_info["user_agent"]}
        session_id = session_manager.create_session(
            result.get("user_id", "unknown"), 
            device_info, 
            client_info["ip_address"]
        )
        
        # Return success page or redirect
        return {
            **result,
            "session_id": session_id,
            "message": "Email verified successfully! You can now log in.",
            "redirect_url": f"{request.base_url}login"
        }
        
    except HTTPException as e:
        # Return user-friendly error
        return {
            "error": str(e.detail),
            "message": "Email verification failed. The link may be expired or invalid.",
            "redirect_url": f"{request.base_url}register"
        }
    except Exception as e:
        return {
            "error": "verification_failed",
            "message": "Email verification failed due to a server error.",
            "redirect_url": f"{request.base_url}register"
        }


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


# =============================================================================
# PROTECTED ENDPOINTS FOR TESTING AUTHENTICATION
# =============================================================================

@router.get(
    "/me",
    summary="Get current user info",
    description="Get information about the currently authenticated user. Requires valid JWT token.",
    response_description="Current user information",
    tags=["Protected Endpoints"],
    dependencies=[Depends(security)],
    responses={
        200: {
            "description": "User information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
                        "email": "user@example.com",
                        "is_active": True,
                        "login_type": "email",
                        "created_at": "2025-08-25T09:20:21.381740+00:00",
                        "message": "Authentication successful!"
                    }
                }
            }
        },
        401: {"description": "Authentication required - invalid or missing JWT token"}
    }
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get information about the currently authenticated user."""
    # Get user from database using the user_id from JWT
    user = db.query(models.User).filter_by(id=current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "login_type": user.login_type,
        "created_at": user.created_at,
        "message": "Authentication successful!"
    }


@router.get(
    "/admin/users",
    summary="List all users (Admin)",
    description="Get a paginated list of all users. Requires admin privileges.",
    response_description="Paginated list of users",
    tags=["Admin Endpoints"],
    responses={
        200: {
            "description": "Users retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "users": [
                            {
                                "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
                                "email": "user@example.com",
                                "is_active": True,
                                "login_type": "email",
                                "created_at": "2025-08-25T09:20:21.381740+00:00"
                            }
                        ],
                        "pagination": {
                            "total": 1,
                            "limit": 10,
                            "offset": 0,
                            "has_more": False
                        },
                        "message": "Retrieved 1 users"
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
        403: {"description": "Admin privileges required"}
    }
)
async def list_all_users(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """Get a paginated list of all users. Requires admin privileges."""
    users = db.query(models.User).offset(offset).limit(limit).all()
    total_count = db.query(models.User).count()
    
    return {
        "users": [
            {
                "user_id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "login_type": user.login_type,
                "created_at": user.created_at
            }
            for user in users
        ],
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        },
        "message": f"Retrieved {len(users)} users"
    }


@router.get(
    "/test/public",
    summary="Test public endpoint",
    description="Test endpoint that doesn't require authentication. Used for testing API connectivity.",
    response_description="Public endpoint response",
    tags=["Test Endpoints"],
    responses={
        200: {
            "description": "Public endpoint accessible",
            "content": {
                "application/json": {
                    "example": {
                        "message": "This is a public endpoint - no authentication required",
                        "timestamp": "2025-08-25T09:58:00.000000+00:00",
                        "status": "public"
                    }
                }
            }
        }
    }
)
async def public_endpoint():
    """Test endpoint that doesn't require authentication."""
    return {
        "message": "This is a public endpoint - no authentication required",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "public"
    }


@router.get(
    "/test/protected",
    summary="Test protected endpoint",
    description="Test endpoint that requires JWT authentication. Used for testing authentication flow.",
    response_description="Protected endpoint response with user info",
    tags=["Test Endpoints"],
    responses={
        200: {
            "description": "Protected endpoint accessible with valid authentication",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Hello user@example.com! This endpoint requires authentication.",
                        "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
                        "timestamp": "2025-08-25T09:58:00.000000+00:00",
                        "status": "authenticated"
                    }
                }
            }
        },
        401: {"description": "Authentication required - invalid or missing JWT token"}
    }
)
async def protected_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test endpoint that requires valid JWT authentication."""
    # Get user from database using the user_id from JWT
    user = db.query(models.User).filter_by(id=current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": f"Hello {user.email}! This endpoint requires authentication.",
        "user_id": user.id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "authenticated"
    }
