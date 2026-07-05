from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from alphaflow.core.models import ConfirmOrdersRequest


def _read(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"runs": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"runs": []}


def append_confirmation(path: Path, payload: ConfirmOrdersRequest) -> dict[str, Any]:
    ledger = _read(path)
    entry = {
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "run_id": payload.run_id,
        "strategy": payload.strategy_spec.model_dump(mode="json"),
        "metrics": payload.metrics.model_dump(),
        "risk": payload.risk.model_dump(),
        "orders": [order.model_dump() for order in payload.orders],
    }
    ledger.setdefault("runs", []).append(entry)
    path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    return entry


def portfolio_status(path: Path) -> dict[str, Any]:
    ledger = _read(path)
    positions: dict[str, dict[str, Any]] = {}
    total_notional = 0.0
    for run in ledger.get("runs", []):
        for order in run.get("orders", []):
            if order.get("side") != "BUY":
                continue
            symbol = order["symbol"]
            qty = int(order.get("estimated_quantity", 0))
            notional = float(order.get("estimated_notional", 0))
            if symbol not in positions:
                positions[symbol] = {"symbol": symbol, "quantity": 0, "notional": 0.0}
            positions[symbol]["quantity"] += qty
            positions[symbol]["notional"] += notional
            total_notional += notional
    return {
        "runs": len(ledger.get("runs", [])),
        "total_notional": round(total_notional, 2),
        "positions": list(positions.values()),
        "last_run": ledger.get("runs", [])[-1] if ledger.get("runs") else None,
    }
