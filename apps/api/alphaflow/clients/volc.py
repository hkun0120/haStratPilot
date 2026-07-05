from __future__ import annotations

import json
from typing import Any

import httpx


class VolcArkClient:
    def __init__(self, api_key: str | None, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    async def extract_strategy_json(self, user_query: str, news_text: str | None = None) -> dict[str, Any] | None:
        if not self.configured:
            return None

        prompt = f"""
You are StratPilot's strategy-spec parser. Return only JSON.
Do not give trading advice. Extract a structured strategy configuration draft.

User query:
{user_query}

Optional news:
{news_text or ""}

JSON fields:
market: "US" | "HK" | "GLOBAL"
theme: short string
benchmark: ticker
strategy_hint: one of cross_sectional_multifactor, ai_infra_momentum, etf_momentum_rotation, hk_tech_rotation, news_event_momentum, defensive_regime_switch, breakout_20d
symbols: array of tickers if explicitly mentioned, otherwise []
max_drawdown: decimal number if mentioned, otherwise null
risk_preference: "low" | "medium" | "high"
"""
        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }
            ],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(f"{self.base_url}/responses", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception:
            return None

        text = _extract_output_text(data)
        if not text:
            return None
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except Exception:
            return None


def _extract_output_text(data: dict[str, Any]) -> str | None:
    if isinstance(data.get("output_text"), str):
        return data["output_text"]
    output = data.get("output")
    if isinstance(output, list):
        parts: list[str] = []
        for item in output:
            content = item.get("content") if isinstance(item, dict) else None
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        text = part.get("text") or part.get("output_text")
                        if text:
                            parts.append(text)
        if parts:
            return "\n".join(parts)
    return None
