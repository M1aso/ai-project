"""
Test notifications service event handling.
Note: This test now focuses on the notifications service itself,
without importing from other services to avoid cross-dependencies.
"""
from services.notifications.app import worker
import services.notifications.app.subscribers  # noqa: F401


def test_user_registered_triggers_email():
    """Test that user registration events trigger welcome emails."""
    worker.clear()
    
    # Simulate receiving a user registration event
    # In the real system, this would come from RabbitMQ
    message = {
        "channel": "email",
        "recipient": "user@example.com",
        "template": "welcome",
        "data": {"name": "Alice"},
        "idempotency_key": "test_user_registered_123"
    }
    
    # Enqueue and process the message
    worker.enqueue(message)
    worker.process()
    
    # Verify email was sent
    sent = worker.providers["email"].sent
    assert sent and sent[0]["recipient"] == "user@example.com"
    assert sent[0]["template"] == "welcome"
