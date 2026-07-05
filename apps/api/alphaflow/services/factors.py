from __future__ import annotations

import numpy as np
import pandas as pd

from alphaflow.data.fundamentals import get_fundamental_score
from alphaflow.services.data_provider import MarketData


FACTOR_COLUMNS = [
    "momentum_5d",
    "momentum_20d",
    "momentum_60d",
    "momentum_120d",
    "trend_ma20",
    "trend_ma60",
    "trend_ma120",
    "volume_strength_20d",
    "volatility_20d",
    "drawdown_60d",
    "relative_strength",
    "rsi_14",
    "breakout_20d",
    "fundamental_quality",
    "fundamental_growth",
    "fundamental_valuation",
    "fundamental_cashflow",
    "event_score",
]


def _rsi(close: pd.Series, window: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _event_score(symbol: str, news_text: str | None) -> float:
    if not news_text:
        return 0.0
    text = news_text.lower()
    positive = ["超预期", "beat", "订单", "order", "ai", "芯片", "cloud", "合作", "guidance", "raise"]
    negative = ["miss", "下调", "调查", "lawsuit", "制裁", "出口管制", "亏损", "降级"]
    symbol_hit = 0.35 if symbol.lower().replace(".hk", "") in text else 0
    score = symbol_hit + sum(word in text for word in positive) * 0.08 - sum(word in text for word in negative) * 0.1
    return float(np.clip(score, -1, 1))


def build_factor_panel(market_data: MarketData, benchmark: str, news_text: str | None = None) -> pd.DataFrame:
    if benchmark in market_data.frames:
        benchmark_close = market_data.frames[benchmark]["close"]
    else:
        benchmark_close = next(iter(market_data.frames.values()))["close"]
    benchmark_return_60 = benchmark_close.pct_change(60)
    rows: list[pd.DataFrame] = []

    for symbol, frame in market_data.frames.items():
        close = frame["close"]
        volume = frame["volume"].replace(0, np.nan)
        daily_return = close.pct_change()
        rolling_max_60 = close.rolling(60).max()
        high_20 = close.rolling(20).max()
        fundamentals = get_fundamental_score(symbol)
        factors = pd.DataFrame(index=frame.index)
        factors["symbol"] = symbol
        factors["momentum_5d"] = close.pct_change(5)
        factors["momentum_20d"] = close.pct_change(20)
        factors["momentum_60d"] = close.pct_change(60)
        factors["momentum_120d"] = close.pct_change(120)
        factors["trend_ma20"] = close / close.rolling(20).mean() - 1
        factors["trend_ma60"] = close / close.rolling(60).mean() - 1
        factors["trend_ma120"] = close / close.rolling(120).mean() - 1
        factors["volume_strength_20d"] = volume / volume.rolling(20).mean()
        factors["volatility_20d"] = daily_return.rolling(20).std()
        factors["drawdown_60d"] = close / rolling_max_60 - 1
        factors["relative_strength"] = close.pct_change(60) - benchmark_return_60.reindex(frame.index)
        factors["rsi_14"] = _rsi(close)
        factors["breakout_20d"] = close / high_20 - 1
        factors["fundamental_quality"] = float(fundamentals["quality"])
        factors["fundamental_growth"] = float(fundamentals["growth"])
        factors["fundamental_valuation"] = float(fundamentals["valuation"])
        factors["fundamental_cashflow"] = float(fundamentals["cashflow"])
        factors["event_score"] = _event_score(symbol, news_text)
        rows.append(factors)

    panel = pd.concat(rows).reset_index(names="date")
    panel = panel.replace([np.inf, -np.inf], np.nan)
    return panel


def score_factors(panel: pd.DataFrame, factor_weights: dict[str, float]) -> pd.DataFrame:
    scored = panel.copy()
    scored["raw_score"] = 0.0
    for factor, weight in factor_weights.items():
        if factor not in scored:
            continue
        values = scored[["date", factor]].copy()
        means = values.groupby("date")[factor].transform("mean")
        stds = values.groupby("date")[factor].transform("std").replace(0, np.nan)
        z = ((values[factor] - means) / stds).fillna(0)
        scored[f"z_{factor}"] = z
        scored["raw_score"] += weight * z
    scored["score"] = scored["raw_score"].round(4)
    return scored


def latest_rankings(scored: pd.DataFrame, as_of: pd.Timestamp, limit: int = 12) -> list[dict]:
    current = scored[scored["date"] <= as_of].sort_values("date").groupby("symbol").tail(1)
    current = current.sort_values("score", ascending=False).head(limit)
    fields = [
        "symbol",
        "score",
        "momentum_20d",
        "momentum_60d",
        "trend_ma60",
        "relative_strength",
        "volatility_20d",
        "drawdown_60d",
        "fundamental_quality",
        "fundamental_growth",
        "fundamental_valuation",
        "event_score",
    ]
    result: list[dict] = []
    for _, row in current[fields].fillna(0).iterrows():
        item = row.to_dict()
        result.append({key: (round(float(value), 4) if key != "symbol" else value) for key, value in item.items()})
    return result
