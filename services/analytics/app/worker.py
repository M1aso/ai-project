import os
from celery import Celery

from .clients.storage import StorageClient

celery_app = Celery(
    "analytics_worker", broker=os.getenv("CELERY_BROKER_URL", "memory://")
)


@celery_app.task
def generate_pdf(name: str, content: str) -> str:
    data = content.encode()
    storage = StorageClient()
    object_name = f"{name}.pdf"
    storage.upload_bytes(data, object_name)
    return storage.presigned_get(object_name)
