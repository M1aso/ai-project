from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


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

    @validator("gender")
    def validate_gender(cls, v):
        if v is not None and v not in {"male", "female", "other"}:
            raise ValueError("invalid gender")
        return v


class ProfileUpdate(ProfileBase):
    first_name: Optional[str] = Field(None, max_length=100)

    class Config:
        orm_mode = True


class ProfileRead(ProfileBase):
    user_id: UUID
    updated_at: datetime

    class Config:
        orm_mode = True


class ExperienceLevelBase(BaseModel):
    label: str = Field(..., max_length=50)
    sequence: int


class ExperienceLevelCreate(ExperienceLevelBase):
    pass


class ExperienceLevelRead(ExperienceLevelBase):
    id: int

    class Config:
        orm_mode = True


class AvatarPresignRequest(BaseModel):
    content_type: str
    size: int


class AvatarPresignResponse(BaseModel):
    upload_url: str
    avatar_url: str
