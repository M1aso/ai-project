from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..schemas import AvatarPresignRequest, AvatarPresignResponse
from ..services.profile_service import get_profile
from ..storage.minio_client import default_client

router = APIRouter(prefix="/api/profile/avatar", tags=["avatar"])
minio = default_client()


def get_current_user(authorization: str = Header(...)):
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="invalid token")
    token = parts[1]
    user_id, _, roles_part = token.partition(":")
    roles = roles_part.split(",") if roles_part else []
    return {"sub": user_id, "roles": roles}


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
    key = f"{current['sub']}.{'jpg' if payload.content_type == 'image/jpeg' else 'png'}"
    upload_url = minio.presign_put(key, payload.content_type)
    avatar_url = minio.file_url(key)
    profile = get_profile(db, current["sub"])
    if not profile:
        raise HTTPException(status_code=404, detail="profile not found")
    profile.avatar_url = avatar_url
    db.commit()
    return AvatarPresignResponse(upload_url=upload_url, avatar_url=avatar_url)
