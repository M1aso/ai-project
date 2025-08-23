from datetime import datetime, timezone
from typing import Dict, Optional

from sqlalchemy.orm import Session

from ..db.models import Profile, ProfileHistory


def get_profile(db: Session, user_id: str) -> Optional[Profile]:
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def update_profile(
    db: Session, user_id: str, data: Dict[str, Optional[str]], actor_id: str
) -> Profile:
    profile = get_profile(db, user_id)
    if not profile:
        if "first_name" not in data or data["first_name"] is None:
            raise ValueError("first_name required")
        profile = Profile(user_id=user_id, first_name=data["first_name"])
        db.add(profile)
    changes = []
    for field, value in data.items():
        if not hasattr(profile, field):
            continue
        old = getattr(profile, field)
        if value != old:
            setattr(profile, field, value)
            changes.append(
                ProfileHistory(
                    user_id=user_id,
                    field=field,
                    old_value=None if old is None else str(old),
                    new_value=None if value is None else str(value),
                    changed_by=actor_id,
                    changed_at=datetime.now(timezone.utc),
                )
            )
    profile.updated_at = datetime.now(timezone.utc)
    for change in changes:
        db.add(change)
    db.commit()
    db.refresh(profile)
    return profile
