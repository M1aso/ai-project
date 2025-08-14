from __future__ import annotations

from queue import Queue
from typing import Dict

from .providers.email import EmailProvider, TransientError, PermanentError
from .providers.sms import SmsProvider
from .providers.push import PushProvider

queue: Queue[Dict] = Queue()
dlq: list[Dict] = []
processed_keys: set[str] = set()
providers = {
    "email": EmailProvider(),
    "sms": SmsProvider(),
    "push": PushProvider(),
}
MAX_RETRIES = 3


def enqueue(message: Dict) -> bool:
    key = message.get("idempotency_key")
    if key and key in processed_keys:
        return False
    message["attempts"] = 0
    if key:
        processed_keys.add(key)
    queue.put(message)
    return True


def process() -> None:
    while not queue.empty():
        msg = queue.get()
        provider = providers[msg["channel"]]
        try:
            provider.send(
                msg["recipient"],
                msg["template"],
                msg.get("data", {}),
                msg.get("idempotency_key"),
            )
        except TransientError:
            msg["attempts"] += 1
            if msg["attempts"] < MAX_RETRIES:
                queue.put(msg)
            else:
                dlq.append(msg)
        except PermanentError:
            dlq.append(msg)


def clear() -> None:
    while not queue.empty():
        queue.get()
    dlq.clear()
    processed_keys.clear()
    for prov in providers.values():
        prov.sent.clear()
