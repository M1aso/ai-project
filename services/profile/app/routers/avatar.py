from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db.database import get_db
from ..schemas import AvatarPresignRequest, AvatarPresignResponse
from ..services.profile_service import get_profile
from ..storage.minio_client import default_client

router = APIRouter(prefix="/api/profile/avatar", tags=["avatar"])
minio = default_client()


@router.post("/presign", response_model=AvatarPresignResponse)
def presign_avatar(
    payload: AvatarPresignRequest,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="file too large")
    if payload.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(status_code=400, detail="invalid content type")
    key = f"{current['user_id']}.{'jpg' if payload.content_type == 'image/jpeg' else 'png'}"
    upload_url = minio.presign_put(key, payload.content_type)
    avatar_url = minio.file_url(key)
    profile = get_profile(db, current["user_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    profile.avatar_url = avatar_url
    db.commit()
    return AvatarPresignResponse(upload_url=upload_url, avatar_url=avatar_url)
