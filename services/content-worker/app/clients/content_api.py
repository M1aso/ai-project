import os
from typing import Any, Dict

import requests


class ContentAPI:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or os.getenv("CONTENT_API_URL", "http://content:8000")

    def update_asset(self, asset_id: str, data: Dict[str, Any]) -> None:
        url = f"{self.base_url}/api/media-assets/{asset_id}"
        resp = requests.patch(url, json=data, timeout=5)
        resp.raise_for_status()
