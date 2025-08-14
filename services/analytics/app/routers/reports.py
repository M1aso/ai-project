import csv
import io
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from openpyxl import Workbook

from ..db.models import Event, get_db

router = APIRouter(prefix="/api/analytics/reports", tags=["reports"])


@router.get("/dau")
def daily_active_users(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    start = datetime.combine(today, datetime.min.time())
    end = start + timedelta(days=1)
    count = (
        db.query(Event.user_id)
        .filter(Event.ts >= start, Event.ts < end)
        .distinct()
        .count()
    )
    return {"dau": count}


@router.get("/events")
def export_events(
    format: str = Query(..., regex="^(csv|xlsx)$"), db: Session = Depends(get_db)
):
    events = db.query(Event).order_by(Event.id).all()
    if format == "csv":

        def generate():
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ts", "user_id", "type", "src"])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            for e in events:
                writer.writerow([e.ts.isoformat(), e.user_id, e.type, e.src or ""])
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)

        return StreamingResponse(generate(), media_type="text/csv")
    if format == "xlsx":
        wb = Workbook()
        ws = wb.active
        ws.append(["ts", "user_id", "type", "src"])
        for e in events:
            ws.append([e.ts.isoformat(), e.user_id, e.type, e.src])
        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    raise HTTPException(status_code=400, detail="unsupported format")
