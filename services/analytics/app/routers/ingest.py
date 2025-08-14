from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db.models import Event, get_db

router = APIRouter(prefix="/api/analytics", tags=["ingest"])

MAX_BATCH_SIZE = 1000


class EventIn(BaseModel):
    ts: datetime
    user_id: str
    type: str
    src: Optional[str] = None
    payload: dict


@router.post("/ingest")
def ingest(events: List[EventIn], db: Session = Depends(get_db)):
    if len(events) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=413, detail="batch too large")
    db.add_all([Event(**e.dict()) for e in events])
    db.commit()
    return {"ingested": len(events)}
