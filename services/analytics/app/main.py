from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    reset_connection()
    yield
    # Shutdown - add any cleanup here if needed


app = FastAPI(
    title="AI Project - Analytics Service",
    description="""
## Analytics and Event Tracking Service

This service provides:
- 📊 **Event Ingestion** - Collect user behavior events
- 📈 **Analytics Reports** - Generate insights and metrics
- 🎯 **Real-time Tracking** - Live event processing
- 📋 **Data Export** - Export analytics data

### Authentication
Most endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Event Ingestion",
            "description": "Collect and process user events"
        },
        {
            "name": "Reports",
            "description": "Generate analytics reports and insights"
        }
    ]
)

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


@app.get("/api/analytics/openapi.json")
def get_openapi():
    """Custom OpenAPI endpoint to work with API gateway prefix rewriting."""
    return app.openapi()


@app.get("/api/analytics/docs")  
def get_docs():
    """Custom docs endpoint to work with API gateway prefix rewriting."""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/api/analytics/openapi.json",
        title=app.title + " - Swagger UI",
    )
