from datetime import datetime, timezone
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
    text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ExperienceLevel(Base):
    __tablename__ = "experience_levels"

    id = Column(Integer, primary_key=True)
    label = Column(String(50), nullable=False)
    sequence = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


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
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
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
    linked_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


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
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    changed_by = Column(String(36))
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )



