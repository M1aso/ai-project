"""
Event emission for auth service using RabbitMQ.
Publishes events to other services via message queue.
"""
from __future__ import annotations
import logging

from .event_publisher import publish_user_registered, publish_password_reset

logger = logging.getLogger(__name__)


def emit_user_registered(email: str, name: str | None = None) -> None:
    """Emit user registration event via RabbitMQ."""
    try:
        success = publish_user_registered(email, name)
        if success:
            logger.info(f"Successfully published user.registered event for {email}")
        else:
            logger.warning(f"Failed to publish user.registered event for {email}")
    except Exception as e:
        logger.error(f"Error publishing user.registered event for {email}: {e}")


def emit_password_reset(email: str, name: str | None = None) -> None:
    """Emit password reset event via RabbitMQ."""
    try:
        success = publish_password_reset(email, name)
        if success:
            logger.info(f"Successfully published auth.password_reset event for {email}")
        else:
            logger.warning(f"Failed to publish auth.password_reset event for {email}")
    except Exception as e:
        logger.error(f"Error publishing auth.password_reset event for {email}: {e}")
