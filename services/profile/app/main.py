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


app = FastAPI(
    title="AI Project - Profile Service",
    description="""
## User Profile Management Service

This service provides:
- 👤 **User Profile Management**
- 🖼️ **Avatar Upload & Management** 
- 👑 **Admin Experience Features**
- 📊 **Profile Analytics**

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
            "name": "Profile",
            "description": "User profile management operations"
        },
        {
            "name": "Avatar", 
            "description": "Avatar upload and management"
        },
        {
            "name": "Admin",
            "description": "Admin experience and management features"
        }
    ]
)
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


@app.get("/api/profile/openapi.json")
def get_openapi():
    """Custom OpenAPI endpoint to work with API gateway prefix rewriting."""
    return app.openapi()


@app.get("/api/profile/docs")  
def get_docs():
    """Custom docs endpoint to work with API gateway prefix rewriting."""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url="/api/profile/openapi.json",
        title=app.title + " - Swagger UI",
    )
