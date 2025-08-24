from time import time

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware

from .db.database import reset_connection
from .routers import ingest, reports

app = FastAPI(title="Analytics Service")

# Include routers
app.include_router(ingest.router)
app.include_router(reports.router)

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


@app.on_event("startup")
async def startup_event():
    """Reset database connection on startup to ensure fresh connection with env vars."""
    reset_connection()


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "analytics"}

@app.get("/api/analytics/healthz")
def api_healthz():
    return {"status": "ok", "service": "analytics"}


@app.get("/readyz")
def readyz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
