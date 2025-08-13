from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from . import tokens


@dataclass
class RefreshToken:
    token: str
    user_id: str
    family: str
    prev_id: Optional[str]
    revoked_at: Optional[datetime]
    expires_at: datetime


_store: Dict[str, RefreshToken] = {}


def issue_token(
    user_id: str, family: str, prev_id: Optional[str] = None
) -> RefreshToken:
    token, expires_at = tokens.create_refresh_token(user_id, family)
    rt = RefreshToken(
        token=token,
        user_id=user_id,
        family=family,
        prev_id=prev_id,
        revoked_at=None,
        expires_at=expires_at,
    )
    _store[token] = rt
    return rt


def rotate(token: str) -> RefreshToken:
    rt = _store.get(token)
    if not rt or rt.revoked_at:
        raise ValueError("invalid token")
    rt.revoked_at = datetime.utcnow()
    return issue_token(rt.user_id, rt.family, prev_id=token)


def revoke_family(family: str) -> None:
    now = datetime.utcnow()
    for rt in _store.values():
        if rt.family == family:
            rt.revoked_at = now


def reset() -> None:
    _store.clear()
