from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..services import email_flows
from ..db.database import get_db


router = APIRouter(prefix="/api/auth")


class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str


class EmailVerifyRequest(BaseModel):
    token: str


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str


@router.post("/email/register")
def register_endpoint(req: EmailRegisterRequest, db: Session = Depends(get_db)):
    email_flows.register(db, req.email, req.password)
    return {"message": "verification sent"}


@router.post("/email/verify")
def verify_endpoint(req: EmailVerifyRequest, db: Session = Depends(get_db)):
    return email_flows.verify(db, req.token)


@router.post("/login")
def login_endpoint(req: EmailLoginRequest, db: Session = Depends(get_db)):
    return email_flows.login(db, req.email, req.password, req.remember_me)


@router.post("/password/reset/request")
def reset_request_endpoint(req: PasswordResetRequest, db: Session = Depends(get_db)):
    email_flows.request_password_reset(db, req.email)
    return {"message": "reset sent"}


@router.post("/password/reset/confirm")
def reset_confirm_endpoint(
    req: PasswordResetConfirmRequest, db: Session = Depends(get_db)
):
    email_flows.confirm_password_reset(db, req.token, req.new_password)
    return {"message": "password reset"}
