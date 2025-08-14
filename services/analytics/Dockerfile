# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder
RUN pip install --prefix=/install --no-cache-dir fastapi uvicorn sqlalchemy prometheus_client openpyxl celery

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app /app/app
USER 1000
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
