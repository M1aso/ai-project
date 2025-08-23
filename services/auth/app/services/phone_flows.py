from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from fastapi import HTTPException

from ..security import rate_limit


@dataclass
class PhoneCode:
    code: str
    sent_at: datetime
    attempts: int = 0
    locked_until: Optional[datetime] = None


_codes: Dict[str, PhoneCode] = {}


def _generate_code() -> str:
    import random

    return f"{random.randint(0,999999):06d}"


def send_code(phone: str, ip: str) -> str:
    rate_limit.check_limits(phone, ip)
    code = _generate_code()
    _codes[phone] = PhoneCode(code=code, sent_at=datetime.now(timezone.utc))
    return code


def verify_code(phone: str, code: str) -> None:
    entry = _codes.get(phone)
    if not entry:
        raise HTTPException(status_code=400, detail="code not requested")
    now = datetime.now(timezone.utc)
    if entry.locked_until and now < entry.locked_until:
        raise HTTPException(status_code=423, detail="phone locked")
    if code != entry.code:
        entry.attempts += 1
        if entry.attempts >= 5:
            entry.locked_until = now + timedelta(hours=1)
            raise HTTPException(status_code=423, detail="phone locked")
        raise HTTPException(status_code=400, detail="invalid code")
    del _codes[phone]


def reset() -> None:
    _codes.clear()
    rate_limit.reset()
