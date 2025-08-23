from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..db import models
from ..security import tokens


def register(db: Session, email: str, password: str) -> str:
    existing = db.query(models.User).filter_by(email=email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        id=str(uuid4()),
        login_type="email",
        email=email,
        password_hash=tokens.hash_password(password),
        is_active=False,
    )
    db.add(user)
    token = tokens.generate_token()
    ev = models.EmailVerification(
        token=token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(ev)
    db.commit()
    return token


def verify(db: Session, token: str) -> dict:
    ev = db.query(models.EmailVerification).filter_by(token=token).first()
    if not ev or ev.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid token")
    user = db.query(models.User).filter_by(id=ev.user_id).first()
    user.is_active = True
    db.delete(ev)
    family = str(uuid4())
    access = tokens.create_access_token(user.id)
    refresh, expires_at = tokens.create_refresh_token(user.id, family)
    rt = models.RefreshToken(
        token=refresh, user_id=user.id, family=family, expires_at=expires_at
    )
    db.add(rt)
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "user_id": user.id}


def login(db: Session, email: str, password: str, remember_me: bool = False) -> dict:
    user = db.query(models.User).filter_by(email=email).first()
    if (
        not user
        or not user.is_active
        or not tokens.verify_password(password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    db.query(models.RefreshToken).filter_by(user_id=user.id).delete()
    family = str(uuid4())
    access = tokens.create_access_token(user.id)
    ttl = 60 if remember_me else 30
    refresh, expires_at = tokens.create_refresh_token(user.id, family, ttl * 24 * 3600)
    rt = models.RefreshToken(
        token=refresh, user_id=user.id, family=family, expires_at=expires_at
    )
    db.add(rt)
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "user_id": user.id}


def request_password_reset(db: Session, email: str) -> str:
    user = db.query(models.User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    token = tokens.generate_token()
    pr = models.PasswordReset(
        token=token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    db.add(pr)
    db.commit()
    return token


def confirm_password_reset(db: Session, token: str, new_password: str) -> None:
    pr = db.query(models.PasswordReset).filter_by(token=token).first()
    if not pr or pr.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid token")
    user = db.query(models.User).filter_by(id=pr.user_id).first()
    user.password_hash = tokens.hash_password(new_password)
    db.query(models.RefreshToken).filter_by(user_id=user.id).delete()
    db.delete(pr)
    db.commit()
