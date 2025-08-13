from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..db.models import ExperienceLevel, get_db
from ..schemas import ExperienceLevelCreate, ExperienceLevelRead

router = APIRouter(prefix="/api/admin/experience-levels", tags=["experience"])


def get_current_user(authorization: str = Header(...)):
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="invalid token")
    token = parts[1]
    user_id, _, roles_part = token.partition(":")
    roles = roles_part.split(",") if roles_part else []
    return {"sub": user_id, "roles": roles}


def require_admin(user=Depends(get_current_user)):
    if "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="forbidden")
    return user


@router.get("", response_model=list[ExperienceLevelRead])
def list_levels(_: dict = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(ExperienceLevel).order_by(ExperienceLevel.sequence).all()


@router.post("", response_model=ExperienceLevelRead)
def create_level(
    payload: ExperienceLevelCreate,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    level = ExperienceLevel(label=payload.label, sequence=payload.sequence)
    db.add(level)
    db.commit()
    db.refresh(level)
    return level


@router.put("/{level_id}", response_model=ExperienceLevelRead)
def update_level(
    level_id: int,
    payload: ExperienceLevelCreate,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    level = db.get(ExperienceLevel, level_id)
    if not level:
        raise HTTPException(status_code=404, detail="not found")
    level.label = payload.label
    level.sequence = payload.sequence
    db.commit()
    db.refresh(level)
    return level


@router.delete("/{level_id}", status_code=204)
def delete_level(
    level_id: int,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    level = db.get(ExperienceLevel, level_id)
    if not level:
        raise HTTPException(status_code=404, detail="not found")
    db.delete(level)
    db.commit()
    return None
