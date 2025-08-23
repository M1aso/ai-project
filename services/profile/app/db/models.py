from datetime import datetime, timezone
import os
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./profile.db")
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


class ExperienceLevel(Base):
    __tablename__ = "experience_levels"

    id = Column(Integer, primary_key=True)
    label = Column(String(50), nullable=False)
    sequence = Column(Integer, nullable=False)


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        CheckConstraint(
            "gender IN ('male','female','other')", name="ck_profiles_gender"
        ),
    )

    user_id = Column(String(36), primary_key=True)
    first_name = Column(String(100), nullable=False)
    nickname = Column(String(50))
    birth_date = Column(Date)
    gender = Column(String(10))
    country = Column(String(100))
    city = Column(String(100))
    company = Column(String(150))
    position = Column(String(150))
    experience_id = Column(Integer, ForeignKey("experience_levels.id"), nullable=True)
    avatar_url = Column(String(255))
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    experience = relationship("ExperienceLevel")


class SocialBinding(Base):
    __tablename__ = "social_bindings"
    __table_args__ = (
        CheckConstraint(
            "provider IN ('telegram','vkontakte','whatsapp')",
            name="ck_social_bindings_provider",
        ),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(
        String(36), ForeignKey("profiles.user_id", ondelete="CASCADE"), nullable=False
    )
    provider = Column(String(20), nullable=False)
    provider_id = Column(String(255))
    linked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class ProfileHistory(Base):
    __tablename__ = "profile_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        String(36), ForeignKey("profiles.user_id", ondelete="CASCADE"), nullable=False
    )
    field = Column(String(50), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    changed_by = Column(String(36))


# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
