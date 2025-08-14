from time import time

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="Analytics Service")

REQUEST_COUNT = Counter(
    "analytics_request_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "analytics_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time()
        response = await call_next(request)
        REQUEST_COUNT.labels(
            request.method, request.url.path, response.status_code
        ).inc()
        REQUEST_LATENCY.labels(request.url.path).observe(time() - start)
        return response


app.add_middleware(MetricsMiddleware)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "analytics"}


@app.get("/readyz")
def readyz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
