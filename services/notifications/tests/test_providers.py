from pathlib import Path

import pytest

import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.notifications.app import worker


@pytest.fixture(autouse=True)
def _clean():
    worker.clear()
    yield
    worker.clear()


def test_retry_transient_error():
    worker.enqueue(
        {
            "channel": "email",
            "recipient": "a@example.com",
            "template": "welcome",
            "data": {"failures": 2},
        }
    )
    worker.process()
    assert len(worker.providers["email"].sent) == 1
    assert worker.dlq == []


def test_dlq_on_permanent_error():
    worker.enqueue(
        {
            "channel": "email",
            "recipient": "a@example.com",
            "template": "welcome",
            "data": {"raise": "permanent"},
        }
    )
    worker.process()
    assert worker.dlq and worker.dlq[0]["data"]["raise"] == "permanent"


def test_idempotency():
    msg = {
        "channel": "email",
        "recipient": "a@example.com",
        "template": "welcome",
        "data": {},
        "idempotency_key": "123",
    }
    assert worker.enqueue(msg) is True
    assert worker.enqueue(msg) is False
