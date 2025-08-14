from pathlib import Path

import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.auth.app import events as auth_events
from services.notifications.app import worker
import services.notifications.app.subscribers  # noqa: F401


def test_user_registered_triggers_email():
    worker.clear()
    auth_events.emit_user_registered("user@example.com", "Alice")
    worker.process()
    sent = worker.providers["email"].sent
    assert sent and sent[0]["recipient"] == "user@example.com"
