import time
from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

# Prometheus metrics
REQUEST_COUNT = Counter(
    "auth_requests_total", "Total HTTP requests", ["method", "path", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "auth_request_duration_seconds", "Request duration in seconds", ["path"]
)

router = APIRouter()


@router.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to record request metrics."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        REQUEST_COUNT.labels(
            request.method, request.url.path, str(response.status_code)
        ).inc()
        REQUEST_LATENCY.labels(request.url.path).observe(time.time() - start)
        return response


def setup_metrics(app):
    """Register metrics middleware and router on the app."""
    app.add_middleware(MetricsMiddleware)
    app.include_router(router)
