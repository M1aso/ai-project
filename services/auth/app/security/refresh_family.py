from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Dict, Optional

from . import tokens


@dataclass
class RefreshToken:
    token: str
    user_id: str
    family: str
    expires_at: datetime
    prev_id: Optional[str] = None
    revoked_at: Optional[datetime] = None


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
    
    # Use dataclasses.replace to create a proper copy with revoked_at set
    revoked_rt = replace(rt, revoked_at=datetime.now(timezone.utc))
    _store[token] = revoked_rt
    
    return issue_token(rt.user_id, rt.family, prev_id=token)


def revoke_family(family: str) -> None:
    now = datetime.now(timezone.utc)
    tokens_to_update = []
    
    # Find tokens to revoke
    for token, rt in _store.items():
        if rt.family == family:
            tokens_to_update.append(token)
    
    # Update each token using dataclasses.replace
    for token in tokens_to_update:
        rt = _store[token]
        revoked_rt = replace(rt, revoked_at=now)
        _store[token] = revoked_rt


def reset() -> None:
    _store.clear()
