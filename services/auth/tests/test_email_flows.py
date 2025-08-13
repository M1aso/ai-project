import os
from pathlib import Path

import pytest
from alembic import command, config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.auth.app.main import app
from services.auth.app.db import models
from services.auth.app.routers import email as email_router


@pytest.fixture(scope="module")
def client():
    cfg = config.Config("services/auth/app/db/migrations/alembic.ini")
    cfg.set_main_option("script_location", "services/auth/app/db/migrations")
    db_url = "sqlite:///./test_auth.db"
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")
    with TestClient(app) as c:
        yield c
    email_router.engine.dispose()
    if os.path.exists("test_auth.db"):
        os.remove("test_auth.db")


def test_email_flows(client):
    # Register
    r = client.post(
        "/api/auth/email/register", json={"email": "u@example.com", "password": "pw"}
    )
    assert r.status_code == 200

    # Invalid verify
    r = client.post("/api/auth/email/verify", json={"token": "bad"})
    assert r.status_code == 400

    # Get verification token from DB
    with Session(email_router.engine) as db:
        tok = db.query(models.EmailVerification).first().token

    r = client.post("/api/auth/email/verify", json={"token": tok})
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    # Login wrong password
    r = client.post(
        "/api/auth/login", json={"email": "u@example.com", "password": "bad"}
    )
    assert r.status_code == 401

    # Login correct
    r = client.post(
        "/api/auth/login", json={"email": "u@example.com", "password": "pw"}
    )
    assert r.status_code == 200

    # Request password reset
    r = client.post("/api/auth/password/reset/request", json={"email": "u@example.com"})
    assert r.status_code == 200
    with Session(email_router.engine) as db:
        pr_tok = db.query(models.PasswordReset).first().token
        refresh_count = db.query(models.RefreshToken).count()
        assert refresh_count > 0

    # Confirm reset
    r = client.post(
        "/api/auth/password/reset/confirm",
        json={"token": pr_tok, "new_password": "newpw"},
    )
    assert r.status_code == 200
    with Session(email_router.engine) as db:
        assert db.query(models.RefreshToken).count() == 0

    # Old password fails
    r = client.post(
        "/api/auth/login", json={"email": "u@example.com", "password": "pw"}
    )
    assert r.status_code == 401

    # New password works
    r = client.post(
        "/api/auth/login", json={"email": "u@example.com", "password": "newpw"}
    )
    assert r.status_code == 200
