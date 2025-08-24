from fastapi import FastAPI

from .db.database import reset_connection
from .metrics import MetricsMiddleware, metrics
from .routers import admin_experience, avatar, profile

app = FastAPI(title="Profile Service")
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(profile.router)
app.include_router(avatar.router)
app.include_router(admin_experience.router)


@app.on_event("startup")
async def startup_event():
    """Reset database connection on startup to ensure fresh connection with env vars."""
    reset_connection()


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "profile"}

@app.get("/api/profile/healthz")
def api_healthz():
    return {"status": "ok", "service": "profile"}


@app.get("/readyz")
def readyz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics_endpoint():
    return metrics()
