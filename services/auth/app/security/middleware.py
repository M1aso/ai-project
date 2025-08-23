from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from .tokens import verify_token

security = HTTPBearer()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify current user from JWT token."""
    try:
        payload = verify_token(credentials.credentials, "access")
        return {
            "user_id": payload["sub"],
            "roles": payload.get("roles", [])
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


def get_optional_user(authorization: str = None):
    """Optional authentication - returns user if token is valid, None otherwise."""
    if not authorization:
        return None
    
    try:
        # Remove "Bearer " prefix if present
        token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
        payload = verify_token(token, "access")
        return {
            "user_id": payload["sub"],
            "roles": payload.get("roles", [])
        }
    except (ValueError, AttributeError):
        return None


def require_roles(*required_roles):
    """Decorator to require specific roles."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_roles = set(current_user.get("roles", []))
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin role."""
    if "admin" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_authenticated(current_user: dict = Depends(get_current_user)):
    """Dependency to require any authenticated user."""
    return current_user
