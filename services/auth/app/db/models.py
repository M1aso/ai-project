from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import declarative_base
from sqlalchemy import event

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    login_type = Column(String(10), nullable=False)
    phone = Column(String(15), unique=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    is_active = Column(Boolean, nullable=False, default=False)
    blocked_until = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )


@event.listens_for(User, 'before_update')
def update_updated_at(mapper, connection, target):
    """Automatically update the updated_at field before any update."""
    target.updated_at = datetime.now(timezone.utc)


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    token = Column(String(64), primary_key=True)
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class PasswordReset(Base):
    __tablename__ = "password_resets"

    token = Column(String(64), primary_key=True)
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String(512), primary_key=True)
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family = Column(String(36), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __table_args__ = (Index("ix_refresh_tokens_user_id_family", "user_id", "family"),)
