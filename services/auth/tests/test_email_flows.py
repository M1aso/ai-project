import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from alembic import command, config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.auth.app.main import app
from services.auth.app.db import models
from services.auth.app.db.database import get_db


# Test database setup
test_engine = None
TestSessionLocal = None


@pytest.fixture(scope="module")
def client():
    global test_engine, TestSessionLocal
    
    # Set up test database
    # Handle both local (from services/auth) and CI (from project root) environments
    import os
    if os.path.exists("app/db/migrations/alembic.ini"):
        # Running from services/auth directory (local)
        alembic_ini_path = "app/db/migrations/alembic.ini"
        script_location = "app/db/migrations"
    else:
        # Running from project root (CI)
        alembic_ini_path = "services/auth/app/db/migrations/alembic.ini"
        script_location = "services/auth/app/db/migrations"
    
    cfg = config.Config(alembic_ini_path)
    cfg.set_main_option("script_location", script_location)
    db_url = "sqlite:///./test_auth.db"
    cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(cfg, "head")
    
    # Create test engine and session
    test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Override the dependency
    def override_get_db():
        try:
            db = TestSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    # Cleanup
    app.dependency_overrides.clear()
    test_engine.dispose()
    if os.path.exists("test_auth.db"):
        os.remove("test_auth.db")


@patch('services.auth.app.services.email_service.email_service.send_verification_email')
@patch('services.auth.app.services.email_service.email_service.send_welcome_email')
def test_email_flows(mock_welcome_email, mock_verification_email, client):
    # Mock email service to return success
    mock_verification_email.return_value = True
    mock_welcome_email.return_value = True
    
    # Register
    r = client.post(
        "/api/auth/email/register", json={"email": "u@example.com", "password": "Password123!"}
    )
    assert r.status_code == 200

    # Invalid verify
    r = client.post("/api/auth/email/verify", json={"token": "invalid_token_that_is_at_least_32_characters_long"})
    assert r.status_code == 400

    # Get verification token from DB
    with Session(test_engine) as db:
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
        "/api/auth/login", json={"email": "u@example.com", "password": "Password123!"}
    )
    assert r.status_code == 200

    # Request password reset
    r = client.post("/api/auth/password/reset/request", json={"email": "u@example.com"})
    assert r.status_code == 200
    with Session(test_engine) as db:
        pr_tok = db.query(models.PasswordReset).first().token
        refresh_count = db.query(models.RefreshToken).count()
        assert refresh_count > 0

    # Confirm reset
    r = client.post(
        "/api/auth/password/reset/confirm",
        json={"token": pr_tok, "new_password": "NewPassword123!"},
    )
    assert r.status_code == 200
    with Session(test_engine) as db:
        assert db.query(models.RefreshToken).count() == 0

    # Old password fails
    r = client.post(
        "/api/auth/login", json={"email": "u@example.com", "password": "Password123!"}
    )
    assert r.status_code == 401

    # New password works
    r = client.post(
        "/api/auth/login", json={"email": "u@example.com", "password": "NewPassword123!"}
    )
    assert r.status_code == 200
