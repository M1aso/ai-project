from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import reset_connection
from .metrics import MetricsMiddleware, metrics
from .routers import email
from .routers import secure_auth
from .security.middleware import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    reset_connection()
    yield
    # Shutdown - add any cleanup here if needed


app = FastAPI(
    title="Auth Service",
    description="Secure Authentication Service with JWT and Session Management",
    version="1.0.0",
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware (configure for your frontend domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Configure for your frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(email.router)  # Keep existing router for backward compatibility
app.include_router(secure_auth.router)  # New secure router


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "auth"}

@app.get("/api/auth/healthz")
def api_healthz():
    return {"status": "ok", "service": "auth"}


@app.get("/readyz")
def readyz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics_endpoint():
    return metrics()
