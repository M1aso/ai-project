from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailVerificationRead(BaseModel):
    token: str
    user_id: UUID
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PasswordResetRead(BaseModel):
    token: str
    user_id: UUID
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRead(BaseModel):
    token: str
    user_id: UUID
    family: UUID
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
