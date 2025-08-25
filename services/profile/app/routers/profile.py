from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db.database import get_db
from ..db.models import ExperienceLevel, ProfileHistory
from ..schemas import ProfileRead, ProfileUpdate, ExperienceLevelRead
from ..services import profile_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileRead)
def read_profile(current=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = profile_service.get_profile(db, current["user_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    return profile


@router.post("", response_model=ProfileRead)
def create_profile(
    payload: ProfileUpdate,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check if profile already exists
    existing_profile = profile_service.get_profile(db, current["user_id"])
    if existing_profile:
        raise HTTPException(status_code=400, detail="profile already exists")
    
    try:
        # Create new profile
        profile_data = payload.model_dump(exclude_unset=True)
        if "first_name" not in profile_data or not profile_data["first_name"]:
            raise ValueError("first_name is required")
        
        return profile_service.update_profile(
            db, current["user_id"], profile_data, current["user_id"]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


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


@router.get("/experience-levels", response_model=list[ExperienceLevelRead])
def list_experience_levels(db: Session = Depends(get_db)):
    """Get all available experience levels for profile creation/update"""
    return db.query(ExperienceLevel).order_by(ExperienceLevel.sequence).all()


@router.get("/history")
def get_profile_history(
    current=Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get profile change history for the current user"""
    history = db.query(ProfileHistory).filter(
        ProfileHistory.user_id == current["user_id"]
    ).order_by(ProfileHistory.changed_at.desc()).limit(50).all()
    
    return {
        "user_id": current["user_id"],
        "changes": [
            {
                "field": h.field,
                "old_value": h.old_value,
                "new_value": h.new_value,
                "changed_at": h.changed_at,
                "changed_by": h.changed_by
            }
            for h in history
        ]
    }
