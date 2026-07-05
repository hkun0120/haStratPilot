from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

import httpx
import numpy as np
import pandas as pd


@dataclass
class MarketData:
    frames: dict[str, pd.DataFrame]
    source: str
    warnings: list[str]

    @property
    def symbols(self) -> list[str]:
        return list(self.frames.keys())

    @property
    def dates(self) -> pd.DatetimeIndex:
        indexes = [frame.index for frame in self.frames.values() if not frame.empty]
        if not indexes:
            return pd.DatetimeIndex([])
        common = indexes[0]
        for idx in indexes[1:]:
            common = common.intersection(idx)
        return common.sort_values()


def _safe_symbol(symbol: str) -> str:
    return symbol.replace("/", "_").replace(".", "_")


def _business_days(start: date, end: date) -> pd.DatetimeIndex:
    return pd.bdate_range(pd.Timestamp(start), pd.Timestamp(end))


def _seed(symbol: str) -> int:
    digest = hashlib.sha256(symbol.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def synthetic_ohlcv(symbol: str, start: date, end: date) -> pd.DataFrame:
    dates = _business_days(start, end)
    rng = np.random.default_rng(_seed(symbol))
    if len(dates) == 0:
        return pd.DataFrame(columns=["open", "high", "low", "close", "adjusted_close", "volume"])

    base_price = 20 + (_seed(symbol) % 250)
    drift = 0.00035 + ((_seed(symbol) % 17) - 8) / 100000
    vol = 0.008 + (_seed(symbol) % 20) / 2500
    if symbol.endswith(".HK"):
        drift *= 0.6
        vol *= 1.15
    if symbol in {"QQQ", "SPY", "2800.HK", "TLT", "GLD", "SHY"}:
        vol *= 0.55

    shocks = rng.normal(drift, vol, len(dates))
    cycle = np.sin(np.linspace(0, 8 * np.pi, len(dates))) * 0.002
    closes = base_price * np.exp(np.cumsum(shocks + cycle))
    opens = closes * (1 + rng.normal(0, vol / 4, len(dates)))
    highs = np.maximum(opens, closes) * (1 + np.abs(rng.normal(0.002, vol / 5, len(dates))))
    lows = np.minimum(opens, closes) * (1 - np.abs(rng.normal(0.002, vol / 5, len(dates))))
    volume_base = 2_000_000 + (_seed(symbol) % 25_000_000)
    volumes = np.maximum(50_000, volume_base * (1 + rng.normal(0, 0.25, len(dates)))).astype(int)

    return pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "adjusted_close": closes,
            "volume": volumes,
        },
        index=dates,
    )


def _read_cache(cache_dir: Path, symbol: str, start: date, end: date) -> pd.DataFrame | None:
    path = cache_dir / f"{_safe_symbol(symbol)}.csv"
    if not path.exists():
        return None
    try:
        frame = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
        sliced = frame.loc[pd.Timestamp(start) : pd.Timestamp(end)]
        expected_days = len(_business_days(start, end))
        min_rows = max(40, int(expected_days * 0.65))
        if len(sliced) < min_rows:
            return None
        return sliced
    except Exception:
        return None


def _write_cache(cache_dir: Path, symbol: str, frame: pd.DataFrame) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{_safe_symbol(symbol)}.csv"
    out = frame.copy()
    out.index.name = "date"
    out.reset_index().to_csv(path, index=False)


def _unix_date(value: date) -> int:
    return int(pd.Timestamp(value).tz_localize("UTC").timestamp())


def _download_yahoo_chart(symbols: list[str], start: date, end: date) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
    }
    period1 = _unix_date(start)
    period2 = _unix_date(end + timedelta(days=1))
    with httpx.Client(timeout=12, follow_redirects=True, headers=headers) as client:
        for symbol in symbols:
            url = (
                f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                f"?period1={period1}&period2={period2}&interval=1d&events=history&includeAdjustedClose=true"
            )
            try:
                response = client.get(url)
                if response.status_code >= 400:
                    continue
                data = response.json()
                result = (data.get("chart", {}).get("result") or [None])[0]
                if not isinstance(result, dict):
                    continue
                timestamps = result.get("timestamp") or []
                quote = ((result.get("indicators") or {}).get("quote") or [None])[0]
                adjusted = ((result.get("indicators") or {}).get("adjclose") or [None])[0]
                if not timestamps or not isinstance(quote, dict):
                    continue
                adjusted_close = (adjusted or {}).get("adjclose") or quote.get("close")
                frame = pd.DataFrame(
                    {
                        "date": pd.to_datetime(timestamps, unit="s").tz_localize("UTC").tz_convert(None).normalize(),
                        "open": quote.get("open"),
                        "high": quote.get("high"),
                        "low": quote.get("low"),
                        "close": quote.get("close"),
                        "adjusted_close": adjusted_close,
                        "volume": quote.get("volume"),
                    }
                )
                frame = frame.set_index("date").dropna(subset=["close"]).sort_index()
                if len(frame) >= 40:
                    frames[symbol] = frame
            except Exception:
                continue
    return frames


def _download_yfinance(symbols: list[str], start: date, end: date) -> dict[str, pd.DataFrame]:
    import yfinance as yf

    frames: dict[str, pd.DataFrame] = {}
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        data = yf.download(
            tickers=" ".join(symbols),
            start=start.isoformat(),
            end=(end + timedelta(days=1)).isoformat(),
            auto_adjust=False,
            progress=False,
            threads=True,
            group_by="ticker",
            timeout=8,
        )
    if data.empty:
        return frames

    for symbol in symbols:
        if len(symbols) == 1:
            raw = data
        elif symbol in data.columns.get_level_values(0):
            raw = data[symbol]
        else:
            continue
        if raw.empty:
            continue
        columns = {col.lower().replace(" ", "_"): col for col in raw.columns}
        close_col = columns.get("close")
        if close_col is None:
            continue
        adjusted_col = columns.get("adj_close") or close_col
        frame = pd.DataFrame(
            {
                "open": raw[columns.get("open", close_col)],
                "high": raw[columns.get("high", close_col)],
                "low": raw[columns.get("low", close_col)],
                "close": raw[close_col],
                "adjusted_close": raw[adjusted_col],
                "volume": raw[columns.get("volume", close_col)],
            }
        )
        frame = frame.dropna(subset=["close"]).sort_index()
        frame.index = pd.to_datetime(frame.index).tz_localize(None)
        if len(frame) >= 40:
            frames[symbol] = frame
    return frames


def _provider_key(provider: str) -> str:
    text = provider.lower().replace(" ", "").replace("_", "").replace("-", "")
    if "yfinance" in text or "yahoo" in text:
        return "yahoo"
    if "stooq" in text:
        return "stooq"
    if "kaggle" in text:
        return "kaggle"
    if "offline" in text or "demo" in text or "synthetic" in text:
        return "offline"
    return text


def _price_providers(data_sources: list[dict[str, Any]] | None) -> tuple[list[str], bool]:
    if not data_sources:
        return ["yahoo", "stooq", "kaggle"], True
    for row in data_sources:
        if row.get("id") != "price_prediction":
            continue
        if not row.get("enabled", True):
            return [], False
        raw_providers = row.get("providers") or []
        if isinstance(raw_providers, str):
            raw_providers = [item.strip() for item in raw_providers.split(",") if item.strip()]
        providers = [_provider_key(str(provider)) for provider in raw_providers]
        providers = [provider for provider in providers if provider]
        return providers or ["yahoo"], True
    return ["yahoo", "stooq", "kaggle"], True


def _download_from_provider(provider: str, symbols: list[str], start: date, end: date) -> dict[str, pd.DataFrame]:
    if provider == "yahoo":
        downloaded = _download_yahoo_chart(symbols, start, end)
        if downloaded:
            return downloaded
        return _download_yfinance(symbols, start, end)
    return {}


def load_market_data(
    symbols: list[str],
    start: date,
    end: date,
    cache_dir: Path,
    data_sources: list[dict[str, Any]] | None = None,
) -> MarketData:
    unique_symbols = list(dict.fromkeys(symbols))
    frames: dict[str, pd.DataFrame] = {}
    warnings: list[str] = []
    source_parts: list[str] = []
    providers, enabled = _price_providers(data_sources)

    if not enabled:
        raise ValueError("价格预测数据源已在系统设置中关闭，无法执行回测。")

    for symbol in unique_symbols:
        cached = _read_cache(cache_dir, symbol, start, end)
        if cached is not None:
            frames[symbol] = cached
    if frames:
        source_parts.append("cache")

    for provider in providers:
        missing = [symbol for symbol in unique_symbols if symbol not in frames]
        if not missing:
            break
        if provider == "kaggle":
            warnings.append("Kaggle 历史行情已配置，但当前未提供 Kaggle REST 数据集端点，已跳过。")
            continue
        if provider == "stooq":
            warnings.append("Stooq 已配置，但当前实现未接入稳定 REST 端点，已跳过。")
            continue
        if provider == "offline":
            for symbol in missing:
                frames[symbol] = synthetic_ohlcv(symbol, start, end)
                warnings.append(f"{symbol} used configured offline demo data")
            source_parts.append("offline")
            break
        try:
            downloaded = _download_from_provider(provider, missing, start, end)
            for symbol, frame in downloaded.items():
                frames[symbol] = frame
                _write_cache(cache_dir, symbol, frame)
            if downloaded:
                source_parts.append("yahoo_chart" if provider == "yahoo" else provider)
            else:
                warnings.append(f"{provider} returned no usable rows for {', '.join(missing[:6])}")
        except Exception as exc:
            warnings.append(f"{provider} failed: {exc}")

    missing = [symbol for symbol in unique_symbols if symbol not in frames]
    if missing:
        detail = "; ".join(warnings[-6:])
        raise ValueError(
            "在线价格数据不可用，且没有可命中的本地缓存。"
            f"缺失 ticker: {', '.join(missing[:12])}。"
            f"已尝试数据源: {', '.join(providers) or 'none'}。"
            f"{'最近错误: ' + detail if detail else ''}"
        )

    cleaned: dict[str, pd.DataFrame] = {}
    for symbol, frame in frames.items():
        if frame.empty:
            continue
        normalized = frame[["open", "high", "low", "close", "adjusted_close", "volume"]].copy()
        normalized = normalized.replace([np.inf, -np.inf], np.nan).dropna(subset=["close"])
        normalized["volume"] = normalized["volume"].fillna(0)
        cleaned[symbol] = normalized

    return MarketData(cleaned, " + ".join(source_parts) or "offline", warnings)
