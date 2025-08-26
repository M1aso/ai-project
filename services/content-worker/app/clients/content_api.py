import os
from typing import Any, Dict

import requests


class ContentAPI:
    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self.base_url = base_url or os.getenv("CONTENT_API_URL", "http://content:8000")
        # For internal service communication, use a service token or API key
        self.api_key = api_key or os.getenv("CONTENT_WORKER_API_KEY", "")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests including authentication"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def update_asset(self, asset_id: str, data: Dict[str, Any]) -> None:
        url = f"{self.base_url}/api/content/media-assets/{asset_id}"  # Fixed URL path
        headers = self._get_headers()
        resp = requests.patch(url, json=data, headers=headers, timeout=5)
        resp.raise_for_status()
