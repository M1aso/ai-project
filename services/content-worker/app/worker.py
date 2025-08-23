from app.celery_app import celery_app

# ensure tasks are registered
from app.tasks import transcode  # noqa: E402,F401

# Expose celery_app for the CLI
__all__ = ["celery_app"]
