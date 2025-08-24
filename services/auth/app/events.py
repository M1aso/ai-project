from __future__ import annotations


# TODO: Fix cross-service dependency - use message queue or HTTP calls instead
# from services.notifications.app.subscribers import event_bus


def emit_user_registered(email: str, name: str | None = None) -> None:
    # TODO: Implement proper event publishing (Redis pub/sub, RabbitMQ, etc.)
    print(f"Event: user.registered - {email}")
    # event_bus.publish("user.registered", {"email": email, "name": name})


def emit_password_reset(email: str, name: str | None = None) -> None:
    # TODO: Implement proper event publishing (Redis pub/sub, RabbitMQ, etc.)
    print(f"Event: auth.password_reset - {email}")
    # event_bus.publish("auth.password_reset", {"email": email, "name": name})
