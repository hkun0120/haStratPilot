from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_DATA_SOURCE_CONFIG: list[dict[str, Any]] = [
    {
        "id": "price_prediction",
        "target": "快速做价格预测",
        "recommended_combo": "yfinance / Stooq + Kaggle 历史行情",
        "reason": "上手最快，样例多，适合离线 Notebook",
        "risk": "数据延迟、复权方式、退市样本偏差",
        "enabled": True,
        "providers": ["yfinance", "Stooq", "Kaggle"],
    },
    {
        "id": "fundamental_factors",
        "target": "做基本面因子",
        "recommended_combo": "SEC Company Facts + FMP / Alpha Vantage Fundamentals",
        "reason": "官方 XBRL 保真，第三方数据便于快速建模",
        "risk": "字段映射、财报期、restatement、点时可得性",
        "enabled": True,
        "providers": ["SEC Company Facts", "FMP", "Alpha Vantage"],
    },
    {
        "id": "event_nlp",
        "target": "做事件驱动 / NLP",
        "recommended_combo": "SEC filings + HKEXnews + Kaggle financial news + GDELT",
        "reason": "公告和新闻文本足够丰富，适合 LLM/RAG/情绪任务",
        "risk": "文本清洗、实体链接、时间戳对齐",
        "enabled": True,
        "providers": ["SEC filings", "HKEXnews", "Kaggle financial news", "GDELT"],
    },
    {
        "id": "macro_timing",
        "target": "做宏观择时",
        "recommended_combo": "FRED + World Bank + IMF + Treasury FiscalData",
        "reason": "宏观变量官方、长期、可解释",
        "risk": "发布滞后和历史修订会影响回测真实性",
        "enabled": True,
        "providers": ["FRED", "World Bank", "IMF", "Treasury FiscalData"],
    },
    {
        "id": "options_volatility",
        "target": "做期权/波动率",
        "recommended_combo": "Cboe 免费指标 + OCC 统计 + Kaggle options 搜索",
        "reason": "可先用 VIX、Put/Call、样例期权数据验证想法",
        "risk": "完整期权链和高频数据通常付费",
        "enabled": False,
        "providers": ["Cboe", "OCC", "Kaggle options"],
    },
]


def read_runtime_config(path: Path, settings: Any) -> dict[str, Any]:
    saved = _load_saved_config(path)
    return {
        "volc_ark": {
            "api_key": _secret_or_env(saved.get("volc_ark", {}).get("api_key"), settings.volc_ark_api_key),
            "model": saved.get("volc_ark", {}).get("model") or settings.volc_ark_model,
            "base_url": saved.get("volc_ark", {}).get("base_url") or settings.volc_ark_base_url,
        },
        "qveris": {
            "api_key": _secret_or_env(saved.get("qveris", {}).get("api_key"), settings.qveris_api_key),
            "base_url": saved.get("qveris", {}).get("base_url") or settings.qveris_base_url,
        },
        "data_sources": _normalize_data_sources(saved.get("data_sources")),
    }


def write_runtime_config(path: Path, payload: dict[str, Any], settings: Any) -> dict[str, Any]:
    saved = _load_saved_config(path)
    next_config = _saved_config_template(settings)
    next_config = _deep_merge(next_config, saved)

    volc_payload = payload.get("volc_ark")
    if isinstance(volc_payload, dict):
        if _is_raw_secret(volc_payload.get("api_key")):
            next_config["volc_ark"]["api_key"] = volc_payload["api_key"].strip()
        if isinstance(volc_payload.get("model"), str) and volc_payload["model"].strip():
            next_config["volc_ark"]["model"] = volc_payload["model"].strip()
        if isinstance(volc_payload.get("base_url"), str) and volc_payload["base_url"].strip():
            next_config["volc_ark"]["base_url"] = volc_payload["base_url"].strip().rstrip("/")

    qveris_payload = payload.get("qveris")
    if isinstance(qveris_payload, dict):
        if _is_raw_secret(qveris_payload.get("api_key")):
            next_config["qveris"]["api_key"] = qveris_payload["api_key"].strip()
        if isinstance(qveris_payload.get("base_url"), str) and qveris_payload["base_url"].strip():
            next_config["qveris"]["base_url"] = qveris_payload["base_url"].strip().rstrip("/")

    if "data_sources" in payload:
        next_config["data_sources"] = _normalize_data_sources(payload.get("data_sources"))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(next_config, ensure_ascii=False, indent=2), encoding="utf-8")
    return read_runtime_config(path, settings)


def public_runtime_config(config: dict[str, Any]) -> dict[str, Any]:
    volc_key = str(config.get("volc_ark", {}).get("api_key") or "")
    qveris_key = str(config.get("qveris", {}).get("api_key") or "")
    return {
        "volc_ark": {
            "api_key": "",
            "api_key_masked": mask_secret(volc_key),
            "configured": bool(volc_key),
            "model": config.get("volc_ark", {}).get("model", ""),
            "base_url": config.get("volc_ark", {}).get("base_url", ""),
        },
        "qveris": {
            "api_key": "",
            "api_key_masked": mask_secret(qveris_key),
            "configured": bool(qveris_key),
            "base_url": config.get("qveris", {}).get("base_url", ""),
        },
        "data_sources": deepcopy(config.get("data_sources", DEFAULT_DATA_SOURCE_CONFIG)),
    }


def mask_secret(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 10:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _saved_config_template(settings: Any) -> dict[str, Any]:
    return {
        "volc_ark": {
            "api_key": "",
            "model": settings.volc_ark_model,
            "base_url": settings.volc_ark_base_url,
        },
        "qveris": {
            "api_key": "",
            "base_url": settings.qveris_base_url,
        },
        "data_sources": deepcopy(DEFAULT_DATA_SOURCE_CONFIG),
    }


def _load_saved_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _normalize_data_sources(value: Any) -> list[dict[str, Any]]:
    supplied_by_id: dict[str, dict[str, Any]] = {}
    rows = value.values() if isinstance(value, dict) else value
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                supplied_by_id[row["id"]] = row

    normalized: list[dict[str, Any]] = []
    for default_row in DEFAULT_DATA_SOURCE_CONFIG:
        row = {**deepcopy(default_row), **supplied_by_id.get(default_row["id"], {})}
        row["enabled"] = bool(row.get("enabled"))
        row["providers"] = _normalize_providers(row)
        normalized.append(row)
    return normalized


def _normalize_providers(row: dict[str, Any]) -> list[str]:
    providers = row.get("providers")
    if isinstance(providers, str):
        return [item.strip() for item in providers.split(",") if item.strip()]
    if isinstance(providers, list):
        return [str(item).strip() for item in providers if str(item).strip()]
    combo = str(row.get("recommended_combo") or "")
    return [item.strip() for item in combo.replace("/", "+").split("+") if item.strip()]


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _secret_or_env(saved_value: Any, env_value: str | None) -> str:
    saved_text = saved_value.strip() if isinstance(saved_value, str) else ""
    return saved_text or env_value or ""


def _is_raw_secret(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text or "..." in text:
        return False
    return set(text) != {"*"}
