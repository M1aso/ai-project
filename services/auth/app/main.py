from fastapi import FastAPI

from .routers import email

app = FastAPI(title="Auth Service")
app.include_router(email.router)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "auth"}
