from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db.database import reset_connection
from .metrics import MetricsMiddleware, metrics
from .routers import admin_experience, avatar, profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    reset_connection()
    yield
    # Shutdown - add any cleanup here if needed


app = FastAPI(title="Profile Service", lifespan=lifespan)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(profile.router)
app.include_router(avatar.router)
app.include_router(admin_experience.router)


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
