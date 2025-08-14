from typing import Any, Dict


class ProviderError(Exception):
    """Base provider error."""


class TransientError(ProviderError):
    """Retryable error."""


class PermanentError(ProviderError):
    """Non-retryable error."""


class EmailProvider:
    sent: list[Dict[str, Any]] = []

    def send(
        self,
        recipient: str,
        template: str,
        data: Dict[str, Any],
        idempotency_key: str | None = None,
    ) -> None:
        if data.get("raise") == "permanent":
            raise PermanentError("hard failure")

        failures = data.get("failures", 0)
        attempt_key = "_attempt"
        current = data.get(attempt_key, 0)
        if current < failures:
            data[attempt_key] = current + 1
            raise TransientError("temporary failure")

        self.sent.append(
            {
                "recipient": recipient,
                "template": template,
                "data": data,
                "idempotency_key": idempotency_key,
            }
        )
