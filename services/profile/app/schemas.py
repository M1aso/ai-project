from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProfileBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    nickname: Optional[str] = Field(None, max_length=50)
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=150)
    position: Optional[str] = Field(None, max_length=150)
    experience_id: Optional[int] = None
    avatar_url: Optional[str] = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in {"male", "female", "other"}:
            raise ValueError("invalid gender")
        return v


class ProfileUpdate(ProfileBase):
    first_name: Optional[str] = Field(None, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class ProfileRead(ProfileBase):
    user_id: UUID
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExperienceLevelBase(BaseModel):
    label: str = Field(..., max_length=50)
    sequence: int


class ExperienceLevelCreate(ExperienceLevelBase):
    pass


class ExperienceLevelRead(ExperienceLevelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AvatarPresignRequest(BaseModel):
    content_type: str
    size: int


class AvatarPresignResponse(BaseModel):
    upload_url: str
    avatar_url: str
