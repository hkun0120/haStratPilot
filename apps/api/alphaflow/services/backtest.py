from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import vectorbt as vbt
from vectorbt.portfolio.enums import Direction, SizeType

from alphaflow.core.models import MetricSummary, OrderPreview, StrategySpec
from alphaflow.services.data_provider import MarketData
from alphaflow.services.factors import latest_rankings, score_factors


@dataclass
class BacktestResult:
    metrics: MetricSummary
    equity_curve: list[dict]
    drawdown_curve: list[dict]
    target_weights: dict[str, float]
    factor_rankings: list[dict]
    orders: list[OrderPreview]
    trade_log: list[dict]


def _weekly_rebalance_dates(dates: pd.DatetimeIndex) -> set[pd.Timestamp]:
    by_week = pd.Series(dates, index=dates).groupby(dates.to_period("W")).max()
    return set(pd.to_datetime(by_week.values))


def _price_matrix(market_data: MarketData, column: str, dates: pd.DatetimeIndex) -> pd.DataFrame:
    data = {}
    for symbol, frame in market_data.frames.items():
        data[symbol] = frame[column].reindex(dates).ffill()
    return pd.DataFrame(data, index=dates)


def _safe_float(value: float | np.floating | None) -> float:
    if value is None or pd.isna(value) or np.isinf(value):
        return 0.0
    return float(value)


def _select_weights(
    scored: pd.DataFrame,
    signal_date: pd.Timestamp,
    spec: StrategySpec,
    close_prices: pd.DataFrame,
) -> dict[str, float]:
    current = scored[scored["date"] <= signal_date].sort_values("date").groupby("symbol").tail(1)
    current = current[current["symbol"].isin(spec.universe)]
    if "trend_ma60" in current:
        filtered = current[current["trend_ma60"].fillna(-1) > -0.02]
        if len(filtered) >= max(2, spec.top_n // 2):
            current = filtered
    current = current.sort_values("score", ascending=False).head(spec.top_n)
    if current.empty:
        return {}

    vol = current.set_index("symbol")["volatility_20d"].replace(0, np.nan).abs()
    inv_vol = (1 / vol).replace([np.inf, -np.inf], np.nan).fillna(1.0)
    raw = inv_vol / inv_vol.sum()
    cash_buffer = spec.risk_limits.cash_buffer
    max_single = spec.risk_limits.max_single_weight
    weights = (raw * (1 - cash_buffer)).clip(upper=max_single)
    if weights.sum() > 0:
        weights = weights / weights.sum() * min(1 - cash_buffer, weights.sum())

    selected = {symbol: round(float(weight), 4) for symbol, weight in weights.items() if weight > 0}
    if spec.benchmark not in selected and spec.benchmark in close_prices:
        used = sum(selected.values())
        benchmark_weight = max(0.0, min(0.15, 1 - cash_buffer - used))
        if benchmark_weight > 0.02:
            selected[spec.benchmark] = round(benchmark_weight, 4)
    return selected


def _build_order_preview(
    spec: StrategySpec,
    target_weights: dict[str, float],
    market_data: MarketData,
    latest_rank: list[dict],
) -> list[OrderPreview]:
    rank_reason = {row["symbol"]: row for row in latest_rank}
    orders: list[OrderPreview] = []
    latest_date = market_data.dates[-1]
    for symbol, weight in sorted(target_weights.items(), key=lambda item: item[1], reverse=True):
        price = float(market_data.frames[symbol].loc[latest_date, "close"]) if symbol in market_data.frames else 0
        notional = spec.initial_cash * weight
        qty = int(notional // price) if price > 0 else 0
        score = rank_reason.get(symbol, {}).get("score", 0)
        orders.append(
            OrderPreview(
                symbol=symbol,
                side="BUY",
                target_weight=round(weight, 4),
                estimated_price=round(price, 4),
                estimated_quantity=qty,
                estimated_notional=round(notional, 2),
                stop_loss=spec.risk_limits.stop_loss,
                reason=f"Target weight from {spec.strategy_name}; latest factor score {score}.",
            )
        )
    return orders


def _build_vectorbt_target_weights(
    scored: pd.DataFrame,
    spec: StrategySpec,
    dates: pd.DatetimeIndex,
    close_prices: pd.DataFrame,
) -> pd.DataFrame:
    target_weights = pd.DataFrame(np.nan, index=dates, columns=close_prices.columns)
    rebalance_dates = _weekly_rebalance_dates(dates)
    for i, current_date in enumerate(dates[:-1]):
        if current_date not in rebalance_dates:
            continue
        target = _select_weights(scored, current_date, spec, close_prices)
        execution_date = dates[i + 1]
        for symbol in close_prices.columns:
            target_weights.loc[execution_date, symbol] = target.get(symbol, 0.0)
    return target_weights


def _trade_log_from_vectorbt(pf: vbt.Portfolio) -> list[dict]:
    try:
        orders = pf.orders.records_readable
    except Exception:
        return []
    trade_log: list[dict] = []
    for _, order in orders.iterrows():
        timestamp = pd.Timestamp(order["Timestamp"])
        trade_log.append(
            {
                "date": timestamp.date().isoformat(),
                "symbol": str(order["Column"]),
                "side": str(order["Side"]).upper(),
                "quantity": round(float(order["Size"]), 4),
                "price": round(float(order["Price"]), 4),
                "notional": round(float(order["Size"] * order["Price"]), 2),
                "fee": round(float(order["Fees"]), 2),
            }
        )
    return trade_log


def _trade_returns_from_vectorbt(pf: vbt.Portfolio) -> list[float]:
    try:
        trades = pf.trades.records_readable
    except Exception:
        return []
    if "Return" not in trades:
        return []
    return [float(value) for value in trades["Return"].replace([np.inf, -np.inf], np.nan).dropna().tolist()]


def run_backtest(market_data: MarketData, factor_panel: pd.DataFrame, spec: StrategySpec) -> BacktestResult:
    scored = score_factors(factor_panel, spec.custom_weights or next_template_weights(spec.strategy_id))
    dates = market_data.dates
    if len(dates) < 80:
        raise ValueError("Not enough market data to run a meaningful backtest.")

    open_prices = _price_matrix(market_data, "open", dates).astype(float)
    close_prices = _price_matrix(market_data, "close", dates).astype(float)
    target_weights = _build_vectorbt_target_weights(scored, spec, dates, close_prices)

    portfolio = vbt.Portfolio.from_orders(
        close=close_prices,
        size=target_weights,
        size_type=SizeType.TargetPercent,
        direction=Direction.LongOnly,
        price=open_prices,
        fees=0.0005,
        slippage=0.0005,
        init_cash=float(spec.initial_cash),
        cash_sharing=True,
        group_by=True,
        call_seq="auto",
        freq="1D",
    )

    equity_series = portfolio.value()
    if isinstance(equity_series, pd.DataFrame):
        equity_series = equity_series.iloc[:, 0]
    equity_series = equity_series.astype(float)
    returns = equity_series.pct_change().dropna()
    drawdown_series = equity_series / equity_series.cummax() - 1
    benchmark_series = close_prices[spec.benchmark] if spec.benchmark in close_prices else close_prices.iloc[:, 0]
    benchmark_return = benchmark_series.iloc[-1] / benchmark_series.iloc[0] - 1
    total_return = equity_series.iloc[-1] / equity_series.iloc[0] - 1
    years = max((equity_series.index[-1] - equity_series.index[0]).days / 365.25, 1 / 365.25)
    annual_return = (1 + total_return) ** (1 / years) - 1 if total_return > -1 else -1
    annual_vol = returns.std() * np.sqrt(252) if not returns.empty else 0
    sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() and not returns.empty else 0
    max_drawdown = float(drawdown_series.min()) if not drawdown_series.empty else 0
    trade_returns = _trade_returns_from_vectorbt(portfolio)
    wins = [value for value in trade_returns if value > 0]
    losses = [abs(value) for value in trade_returns if value < 0]
    win_rate = float(np.mean([value > 0 for value in trade_returns])) if trade_returns else 0
    pl_ratio = (float(np.mean(wins)) / float(np.mean(losses))) if wins and losses else 0
    calmar = annual_return / abs(max_drawdown) if max_drawdown < 0 else 0
    trade_log = _trade_log_from_vectorbt(portfolio)
    turnover = (
        sum(abs(row["notional"]) for row in trade_log) / max(float(equity_series.mean()), 1) / max(len(target_weights.dropna(how="all")), 1)
        if trade_log
        else 0
    )

    metrics = MetricSummary(
        total_return=round(_safe_float(total_return), 4),
        annual_return=round(_safe_float(annual_return), 4),
        benchmark_return=round(_safe_float(benchmark_return), 4),
        excess_return=round(_safe_float(total_return - benchmark_return), 4),
        max_drawdown=round(_safe_float(max_drawdown), 4),
        annual_volatility=round(_safe_float(annual_vol), 4),
        sharpe_ratio=round(_safe_float(sharpe), 4),
        calmar_ratio=round(_safe_float(calmar), 4),
        win_rate=round(_safe_float(win_rate), 4),
        profit_loss_ratio=round(_safe_float(pl_ratio), 4),
        turnover=round(_safe_float(turnover), 4),
        number_of_trades=len(trade_log),
        best_trade=round(_safe_float(max(trade_returns) if trade_returns else 0), 4),
        worst_trade=round(_safe_float(min(trade_returns) if trade_returns else 0), 4),
    )

    equity = [
        {"date": pd.Timestamp(index).date().isoformat(), "value": round(float(value), 2)}
        for index, value in equity_series.items()
    ]
    drawdowns = [
        {"date": pd.Timestamp(index).date().isoformat(), "drawdown": round(float(value), 4)}
        for index, value in drawdown_series.items()
    ]
    latest_rank = latest_rankings(scored, dates[-1], limit=12)
    final_weights = _select_weights(scored, dates[-1], spec, close_prices)
    orders = _build_order_preview(spec, final_weights, market_data, latest_rank)

    return BacktestResult(
        metrics=metrics,
        equity_curve=equity,
        drawdown_curve=drawdowns,
        target_weights=final_weights,
        factor_rankings=latest_rank,
        orders=orders,
        trade_log=trade_log,
    )


def next_template_weights(strategy_id: str) -> dict[str, float]:
    from alphaflow.services.strategies import get_template

    return get_template(strategy_id).factor_weights
