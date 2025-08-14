from __future__ import annotations

from typing import Any, Callable, Dict

from . import worker


class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[str, list[Callable[[Dict[str, Any]], None]]] = {}

    def subscribe(self, event: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        self._subs.setdefault(event, []).append(handler)

    def publish(self, event: str, payload: Dict[str, Any]) -> None:
        for handler in self._subs.get(event, []):
            handler(payload)


event_bus = EventBus()


def handle_user_registered(payload: Dict[str, Any]) -> None:
    worker.enqueue(
        {
            "channel": "email",
            "recipient": payload["email"],
            "template": "welcome",
            "data": {"user_name": payload.get("name", "user")},
        }
    )


def handle_password_reset(payload: Dict[str, Any]) -> None:
    worker.enqueue(
        {
            "channel": "email",
            "recipient": payload["email"],
            "template": "welcome",
            "data": {"user_name": payload.get("name", "user")},
        }
    )


def handle_content_published(payload: Dict[str, Any]) -> None:
    worker.enqueue(
        {
            "channel": "email",
            "recipient": payload["email"],
            "template": "welcome",
            "data": {"user_name": payload.get("name", "user")},
        }
    )


event_bus.subscribe("user.registered", handle_user_registered)
event_bus.subscribe("auth.password_reset", handle_password_reset)
event_bus.subscribe("content.published", handle_content_published)
