from typing import Tuple

ACCESS_TOKEN_TTL = 3600
REFRESH_TOKEN_TTL = 30 * 24 * 3600


def generate_token() -> str:
    import secrets

    return secrets.token_hex(32)


def hash_password(password: str) -> str:
    import hashlib

    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_access_token(user_id: str, expires_in: int = ACCESS_TOKEN_TTL) -> str:
    return generate_token()


def create_refresh_token(
    user_id: str, family: str, expires_in: int = REFRESH_TOKEN_TTL
) -> Tuple[str, object]:
    from datetime import datetime, timedelta

    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    return token, expires_at
