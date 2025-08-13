from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import HTTPException


class WindowRateLimiter:
    """Simple in-memory sliding window rate limiter."""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window = timedelta(seconds=window_seconds)
        self._history: Dict[str, List[datetime]] = {}

    def check(self, key: str) -> bool:
        now = datetime.utcnow()
        items = self._history.get(key, [])
        items = [t for t in items if now - t < self.window]
        if len(items) >= self.limit:
            self._history[key] = items
            return False
        items.append(now)
        self._history[key] = items
        return True

    def reset(self) -> None:
        self._history.clear()


phone_limiter = WindowRateLimiter(limit=1, window_seconds=30)
ip_limiter = WindowRateLimiter(limit=5, window_seconds=3600)


def check_limits(phone: str, ip: str) -> None:
    """Raise HTTPException if phone or IP exceed limits."""
    if not phone_limiter.check(phone):
        raise HTTPException(status_code=429, detail="Too many requests for phone")
    if not ip_limiter.check(ip):
        raise HTTPException(status_code=429, detail="Too many requests for IP")


def reset() -> None:
    """Reset limiter state (used in tests)."""
    phone_limiter.reset()
    ip_limiter.reset()
