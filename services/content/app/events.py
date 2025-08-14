from __future__ import annotations

from services.notifications.app.subscribers import event_bus


def emit_content_published(email: str, name: str | None = None) -> None:
    event_bus.publish("content.published", {"email": email, "name": name})
