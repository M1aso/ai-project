from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from ..worker import enqueue

router = APIRouter(prefix="/api/notify", tags=["notify"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
ENV = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


class Notification(BaseModel):
    channel: str
    recipient: str | None = None
    template: str
    data: Dict = {}
    idempotency_key: str | None = None


@router.post("/send", status_code=202)
def send_notification(payload: Notification):
    enqueue(payload.dict())
    return {"status": "queued"}


@router.post("/preview")
def preview_notification(payload: Notification):
    ext_map = {"email": "mjml", "sms": "txt", "push": "json"}
    ext = ext_map.get(payload.channel)
    if not ext:
        raise HTTPException(status_code=400, detail="unknown channel")
    template_name = f"{payload.channel}/{payload.template}.{ext}"
    try:
        template = ENV.get_template(template_name)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=404, detail="template not found") from exc
    rendered = template.render(**payload.data)
    return {"rendered": rendered}
