# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder
WORKDIR /tmp
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app /app/app
USER 1000
CMD ["celery", "-A", "app.worker.celery_app", "worker", "-Q", "content-transcode", "--loglevel=info"]
