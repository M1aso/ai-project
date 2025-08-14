import os
from celery import Celery
from kombu import Queue

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery("content_worker", broker=RABBITMQ_URL, backend=RESULT_BACKEND)
celery_app.conf.task_queues = (Queue("content-transcode", durable=True),)
celery_app.conf.task_default_queue = "content-transcode"

# ensure tasks are registered
from app.tasks import transcode  # noqa: E402,F401
