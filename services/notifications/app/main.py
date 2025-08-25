from fastapi import FastAPI

from .routers import notify

app = FastAPI(
    title="AI Project - Notifications Service",
    description="""
## Multi-Channel Notification Service

This service provides:
- 📧 **Email Notifications** - Welcome emails, alerts, newsletters
- 📱 **Push Notifications** - Mobile and web push messages
- 📲 **SMS Notifications** - Text message alerts
- 🔔 **Real-time Notifications** - Instant notification delivery

### Authentication
Most endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Notifications",
            "description": "Send and manage notifications across all channels"
        }
    ]
)
app.include_router(notify.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "notifications"}


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "notifications"}

@app.get("/api/healthz")
def api_healthz():
    return {"status": "ok", "service": "notifications"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


@app.get("/metrics")
def metrics():  # pragma: no cover - placeholder
    return ""


@app.get("/api/notifications/openapi.json")
def get_openapi():
    """Custom OpenAPI endpoint to work with API gateway prefix rewriting."""
    return app.openapi()


@app.get("/api/notifications/docs")  
def get_docs():
    """Custom docs endpoint to work with API gateway prefix rewriting."""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/api/notifications/openapi.json",
        title=app.title + " - Swagger UI",
    )
