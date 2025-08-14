from __future__ import annotations


from services.notifications.app.subscribers import event_bus


def emit_user_registered(email: str, name: str | None = None) -> None:
    event_bus.publish("user.registered", {"email": email, "name": name})


def emit_password_reset(email: str, name: str | None = None) -> None:
    event_bus.publish("auth.password_reset", {"email": email, "name": name})
