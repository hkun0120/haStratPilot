from __future__ import annotations

from typing import Any

from fastapi import Body, HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alphaflow.clients.qveris import QVerisClient
from alphaflow.clients.volc import VolcArkClient
from alphaflow.core.config import get_settings
from alphaflow.core.models import AgentRunRequest, ConfirmOrdersRequest
from alphaflow.services.agent import run_agent
from alphaflow.services.industry_research import get_industry_chain
from alphaflow.services.news import HOT_NEWS
from alphaflow.services.strategies import STRATEGY_TEMPLATES
from alphaflow.storage.config_store import public_runtime_config, read_runtime_config, write_runtime_config
from alphaflow.storage.ledger import append_confirmation, portfolio_status

settings = get_settings()

app = FastAPI(title="StratPilot API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def volc_client() -> VolcArkClient:
    config = read_runtime_config(settings.runtime_config_path, settings)
    return VolcArkClient(
        config["volc_ark"]["api_key"],
        config["volc_ark"]["base_url"],
        config["volc_ark"]["model"],
    )


def qveris_client() -> QVerisClient:
    config = read_runtime_config(settings.runtime_config_path, settings)
    return QVerisClient(config["qveris"]["api_key"], config["qveris"]["base_url"])


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "app": settings.app_name}


@app.get("/api/strategy/templates")
async def strategy_templates() -> dict:
    return {"templates": [template.model_dump() for template in STRATEGY_TEMPLATES]}


@app.get("/api/news/hotspots")
async def news_hotspots() -> dict:
    return {"items": HOT_NEWS}


@app.get("/api/research/industry-chain")
async def industry_chain(theme: str = "ai", language: str = "zh"):
    return get_industry_chain(theme, language)


@app.get("/api/qveris/status")
async def qveris_status() -> dict:
    return await qveris_client().status()


@app.get("/api/system/status")
async def system_status() -> dict:
    config = read_runtime_config(settings.runtime_config_path, settings)
    return {
        "volc_ark": {
            "configured": bool(config["volc_ark"]["api_key"]),
            "model": config["volc_ark"]["model"],
            "base_url": config["volc_ark"]["base_url"],
        },
        "qveris": await qveris_client().status(),
        "paper_trading_only": True,
        "backtest_engine": "vectorbt 0.28.2",
    }


@app.get("/api/system/config")
async def system_config() -> dict[str, Any]:
    config = read_runtime_config(settings.runtime_config_path, settings)
    return public_runtime_config(config)


@app.post("/api/system/config")
async def update_system_config(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    config = write_runtime_config(settings.runtime_config_path, payload, settings)
    return public_runtime_config(config)


@app.post("/api/agent/run")
async def agent_run(request: AgentRunRequest):
    config = read_runtime_config(settings.runtime_config_path, settings)
    try:
        return await run_agent(request, settings.data_cache_dir, volc_client(), qveris_client(), config["data_sources"])
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/orders/confirm")
async def confirm_orders(request: ConfirmOrdersRequest) -> dict:
    entry = append_confirmation(settings.ledger_path, request)
    return {"ok": True, "entry": entry}


@app.get("/api/portfolio/status")
async def get_portfolio_status() -> dict:
    return portfolio_status(settings.ledger_path)
