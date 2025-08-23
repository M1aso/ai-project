import secrets
import os
from typing import Tuple
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Use proper password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration - use environment variables in production
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = int(os.getenv("ACCESS_TOKEN_TTL", 3600))  # 1 hour
REFRESH_TOKEN_TTL = int(os.getenv("REFRESH_TOKEN_TTL", 30 * 24 * 3600))  # 30 days


def generate_token() -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_hex(32)


def hash_password(password: str) -> str:
    """Hash password using bcrypt with proper salt."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    return pwd_context.verify(password, hashed)


def create_access_token(user_id: str, roles: list = None, expires_in: int = ACCESS_TOKEN_TTL) -> str:
    """Create JWT access token with proper claims."""
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "type": "access",
        "roles": roles or []
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(
    user_id: str, family: str, expires_in: int = REFRESH_TOKEN_TTL
) -> Tuple[str, datetime]:
    """Create JWT refresh token."""
    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=expires_in)
    payload = {
        "sub": user_id,
        "family": family,
        "iat": now,
        "exp": expires_at,
        "type": "refresh"
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, expires_at


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != token_type:
            raise jwt.InvalidTokenError("Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
