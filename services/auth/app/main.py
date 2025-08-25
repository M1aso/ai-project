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
    title="AI Project - Authentication Service",
    description="""
## Secure Authentication Service with JWT and Session Management

This service provides:
- 🔐 **User Registration & Email Verification**
- 🔑 **JWT-based Authentication** (Access & Refresh Tokens)
- 👤 **User Profile Management**
- 🛡️ **Rate Limiting & Security**
- 📊 **Session Management**

### Authentication
Most endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Endpoint Categories
- **Public Endpoints**: No authentication required (registration, verification, etc.)
- **Protected Endpoints**: Require valid JWT token
- **Admin Endpoints**: Require admin privileges
- **Test Endpoints**: For testing authentication flow
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Public Endpoints",
            "description": "Endpoints that don't require authentication"
        },
        {
            "name": "Protected Endpoints", 
            "description": "Endpoints that require valid JWT authentication"
        },
        {
            "name": "Admin Endpoints",
            "description": "Endpoints that require admin privileges"
        },
        {
            "name": "Test Endpoints",
            "description": "Test endpoints for development and debugging"
        },
        {
            "name": "Authentication",
            "description": "Core authentication operations"
        }
    ]
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
app.include_router(secure_auth.router)  # New secure router (takes precedence)
app.include_router(email.router)  # Keep existing router for backward compatibility


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


@app.get("/api/auth/openapi.json")
def get_openapi():
    """Custom OpenAPI endpoint to work with API gateway prefix rewriting."""
    return app.openapi()


@app.get("/api/auth/docs")  
def get_docs():
    """Custom docs endpoint to work with API gateway prefix rewriting."""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/api/auth/openapi.json",
        title=app.title + " - Swagger UI",
    )
