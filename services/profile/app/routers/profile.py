from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..schemas import ProfileRead, ProfileUpdate
from ..services import profile_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


def get_current_user(authorization: str = Header(...)):
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="invalid token")
    token = parts[1]
    user_id, _, roles_part = token.partition(":")
    roles = roles_part.split(",") if roles_part else []
    return {"sub": user_id, "roles": roles}


@router.get("", response_model=ProfileRead)
def read_profile(current=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = profile_service.get_profile(db, current["sub"])
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    return profile


@router.put("", response_model=ProfileRead)
def update_profile(
    payload: ProfileUpdate,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return profile_service.update_profile(
            db, current["sub"], payload.model_dump(exclude_unset=True), current["sub"]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
