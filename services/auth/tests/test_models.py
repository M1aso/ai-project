import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from alembic import command, config
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.auth.app.db import models


@pytest.fixture(scope="module")
def engine():
    cfg = config.Config("services/auth/app/db/migrations/alembic.ini")
    cfg.set_main_option("script_location", "services/auth/app/db/migrations")
    db_path = "sqlite:///./test_auth.db"
    cfg.set_main_option("sqlalchemy.url", db_path)
    command.upgrade(cfg, "head")
    eng = create_engine(db_path)
    yield eng
    eng.dispose()
    if os.path.exists("test_auth.db"):
        os.remove("test_auth.db")


@pytest.fixture()
def db(engine):
    with Session(engine) as session:
        yield session


def test_unique_user_email(db):
    user1 = models.User(
        id=str(uuid.uuid4()),
        login_type="email",
        email="a@example.com",
        password_hash="x",
    )
    db.add(user1)
    db.commit()
    user2 = models.User(
        id=str(uuid.uuid4()),
        login_type="email",
        email="a@example.com",
        password_hash="y",
    )
    db.add(user2)
    with pytest.raises(IntegrityError):
        db.commit()


def test_unique_tokens(db):
    user = models.User(
        id=str(uuid.uuid4()),
        login_type="email",
        email="b@example.com",
        password_hash="x",
    )
    db.add(user)
    db.commit()

    ev1 = models.EmailVerification(
        token="tok", user_id=user.id, expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(ev1)
    db.commit()
    db.expunge(ev1)
    ev2 = models.EmailVerification(
        token="tok", user_id=user.id, expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(ev2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

    pr1 = models.PasswordReset(
        token="rtok", user_id=user.id, expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(pr1)
    db.commit()
    db.expunge(pr1)
    pr2 = models.PasswordReset(
        token="rtok", user_id=user.id, expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(pr2)

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_refresh_token_index(engine):
    inspector = inspect(engine)
    indexes = inspector.get_indexes("refresh_tokens")
    assert any(idx["name"] == "ix_refresh_tokens_user_id_family" for idx in indexes)
