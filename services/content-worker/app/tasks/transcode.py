import logging
import subprocess
import time
from pathlib import Path

import yaml
from prometheus_client import Counter

from app.clients.content_api import ContentAPI
from app.celery_app import celery_app

logger = logging.getLogger(__name__)
retry_counter = Counter(
    "transcode_retries_total", "Total transcode retries", ["preset"]
)

PRESETS_PATH = Path(__file__).resolve().parents[1] / "presets.yaml"
with open(PRESETS_PATH, "r", encoding="utf-8") as f:
    PRESETS = yaml.safe_load(f)


@celery_app.task
def transcode_video(
    asset_id: str, source_path: str, preset: str, *, client=None, max_retries: int = 3
):
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset {preset}")
    client = client or ContentAPI()
    ff_args = PRESETS[preset]["ffmpeg_args"]
    src = Path(source_path)
    output_path = str(src.with_name(f"{src.stem}_{preset}.m3u8"))
    cmd = ["ffmpeg", "-y", "-i", source_path] + ff_args + [output_path]

    for attempt in range(max_retries + 1):
        try:
            subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            client.update_asset(
                asset_id, {"status": "ready", "renditions": {preset: output_path}}
            )
            return output_path
        except Exception as exc:  # noqa: BLE001
            logger.warning("transcode attempt %s failed: %s", attempt + 1, exc)
            retry_counter.labels(preset=preset).inc()
            if attempt < max_retries:
                time.sleep(2**attempt)
                continue
            client.update_asset(asset_id, {"status": "failed", "error": str(exc)})
            raise


__all__ = ["transcode_video"]
