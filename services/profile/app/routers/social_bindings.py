from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from ..auth import get_current_user
from ..db.database import get_db
from ..db.models import SocialBinding
from ..services import profile_service

router = APIRouter(prefix="/api/profile/social", tags=["social"])


class SocialBindingCreate(BaseModel):
    provider: str
    provider_id: str


class SocialBindingRead(BaseModel):
    id: str
    provider: str
    provider_id: str
    linked_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[SocialBindingRead])
def list_social_bindings(
    current=Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get all social bindings for the current user"""
    # First ensure profile exists
    profile = profile_service.get_profile(db, current["user_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    
    bindings = db.query(SocialBinding).filter(
        SocialBinding.user_id == current["user_id"]
    ).all()
    
    return bindings


@router.post("", response_model=SocialBindingRead)
def create_social_binding(
    payload: SocialBindingCreate,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new social binding"""
    # Validate provider
    if payload.provider not in ["telegram", "vkontakte", "whatsapp"]:
        raise HTTPException(status_code=400, detail="invalid provider")
    
    # Ensure profile exists
    profile = profile_service.get_profile(db, current["user_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    
    # Check if binding already exists
    existing = db.query(SocialBinding).filter(
        SocialBinding.user_id == current["user_id"],
        SocialBinding.provider == payload.provider
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="binding already exists for this provider")
    
    # Create new binding
    binding = SocialBinding(
        user_id=current["user_id"],
        provider=payload.provider,
        provider_id=payload.provider_id
    )
    
    db.add(binding)
    db.commit()
    db.refresh(binding)
    
    return binding


@router.delete("/{binding_id}")
def delete_social_binding(
    binding_id: str,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a social binding"""
    binding = db.query(SocialBinding).filter(
        SocialBinding.id == binding_id,
        SocialBinding.user_id == current["user_id"]
    ).first()
    
    if not binding:
        raise HTTPException(status_code=404, detail="binding not found")
    
    db.delete(binding)
    db.commit()
    
    return {"message": "binding removed successfully"}
