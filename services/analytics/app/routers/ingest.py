from datetime import datetime
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import Event
from ..auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["ingest"])

MAX_BATCH_SIZE = 1000


class EventIn(BaseModel):
    ts: datetime
    user_id: str
    type: str
    src: Optional[str] = None
    payload: dict


@router.post("/ingest")
def ingest(
    events: List[EventIn], 
    db: Session = Depends(get_db),
    current_user: Dict[str, any] = Depends(get_current_user)
):
    if len(events) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=413, detail="batch too large")
    db.add_all([Event(**e.model_dump()) for e in events])
    db.commit()
    return {"ingested": len(events)}
