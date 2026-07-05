from __future__ import annotations

from typing import Any

import httpx


class QVerisClient:
    def __init__(self, api_key: str | None, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def status(self) -> dict[str, Any]:
        if not self.configured:
            return {"configured": False, "mode": "not_configured", "message": "QVeris API key not found in env."}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        candidates = ["/auth/credits/ledger", "/auth/usage/history/v2", "/credits", "/account/credits"]
        async with httpx.AsyncClient(timeout=8) as client:
            for path in candidates:
                try:
                    response = await client.get(f"{self.base_url}{path}", headers=headers, params={"summary": "true"})
                    if response.status_code < 400:
                        return {"configured": True, "mode": "rest", "credits": response.json(), "endpoint": path}
                except Exception:
                    continue
        return {"configured": True, "mode": "rest_unverified", "message": "QVeris key present; REST status endpoint was not reachable."}

    async def discover(self, query: str, limit: int = 3) -> dict[str, Any]:
        if not self.configured:
            return {"configured": False, "results": []}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"query": query, "limit": limit}
        candidates = ["/search", "/discover", "/tools/search", "/agent/discover"]
        async with httpx.AsyncClient(timeout=15) as client:
            for path in candidates:
                try:
                    response = await client.post(f"{self.base_url}{path}", headers=headers, json=payload)
                    if response.status_code < 400:
                        data = response.json()
                        if isinstance(data, dict):
                            data.setdefault("configured", True)
                            data.setdefault("mode", "rest")
                            data.setdefault("endpoint", path)
                            return data
                except Exception:
                    continue
        return {"configured": True, "mode": "rest", "results": [], "message": "REST discovery endpoint failed; falling back to built-in data sources."}
