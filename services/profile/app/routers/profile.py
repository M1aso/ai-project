from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db.database import get_db
from ..schemas import ProfileRead, ProfileUpdate
from ..services import profile_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileRead)
def read_profile(current=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = profile_service.get_profile(db, current["user_id"])
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
            db, current["user_id"], payload.model_dump(exclude_unset=True), current["user_id"]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
