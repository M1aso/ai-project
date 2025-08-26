import os
import jwt
from typing import Optional, Dict
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT configuration - should match auth service
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-not-for-production-change-in-prod")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode JWT token (same logic as auth service)."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != token_type:
            raise jwt.InvalidTokenError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, any]:
    """Extract and verify current user from JWT token."""
    try:
        payload = verify_token(credentials.credentials, "access")
        return {
            "user_id": payload["sub"],
            "roles": payload.get("roles", [])
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


def get_optional_user(authorization: Optional[str] = None) -> Optional[Dict[str, any]]:
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
