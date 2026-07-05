from alphaflow.core.models import MetricSummary, RiskLimits, RiskVerdict


def evaluate_risk(metrics: MetricSummary, limits: RiskLimits) -> RiskVerdict:
    hard_reasons: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []

    def add_check(name: str, passed: bool, value: float | int, limit: float | int, severity: str) -> None:
        checks.append({"name": name, "passed": passed, "value": value, "limit": limit, "severity": severity})

    drawdown_ok = abs(metrics.max_drawdown) <= limits.max_portfolio_drawdown
    add_check("Max drawdown", drawdown_ok, abs(metrics.max_drawdown), limits.max_portfolio_drawdown, "hard")
    if not drawdown_ok:
        hard_reasons.append(
            f"Backtest max drawdown {abs(metrics.max_drawdown):.1%} exceeds user limit {limits.max_portfolio_drawdown:.1%}."
        )

    sharpe_ok = metrics.sharpe_ratio >= limits.min_sharpe
    add_check("Sharpe ratio", sharpe_ok, metrics.sharpe_ratio, limits.min_sharpe, "warn")
    if not sharpe_ok:
        warnings.append(f"Sharpe ratio {metrics.sharpe_ratio:.2f} is below threshold {limits.min_sharpe:.2f}.")

    trades_ok = metrics.number_of_trades >= limits.min_trades
    add_check("Trade sample", trades_ok, metrics.number_of_trades, limits.min_trades, "warn")
    if not trades_ok:
        warnings.append(f"Only {metrics.number_of_trades} simulated trades; sample size is thin.")

    benchmark_ok = metrics.excess_return >= 0
    add_check("Benchmark comparison", benchmark_ok, metrics.excess_return, 0, "warn")
    if not benchmark_ok:
        warnings.append(f"Strategy underperformed benchmark by {abs(metrics.excess_return):.1%}.")

    vol_ok = metrics.annual_volatility <= 0.45
    add_check("Annual volatility", vol_ok, metrics.annual_volatility, 0.45, "warn")
    if not vol_ok:
        warnings.append(f"Annualized volatility {metrics.annual_volatility:.1%} is elevated.")

    if hard_reasons:
        return RiskVerdict(
            allow_trade=False,
            decision="REJECT",
            reasons=hard_reasons + warnings,
            suggested_action="Reduce concentration, increase cash buffer, or re-run with a lower-volatility template.",
            checks=checks,
        )
    if warnings:
        return RiskVerdict(
            allow_trade=True,
            decision="WATCH",
            reasons=warnings,
            suggested_action="Use smaller position size, keep stop rules, and monitor the next rebalance.",
            checks=checks,
        )
    return RiskVerdict(
        allow_trade=True,
        decision="ALLOW",
        reasons=["Backtest risk checks passed under the selected constraints."],
        suggested_action="Proceed only after user confirms the simulated order preview.",
        checks=checks,
    )
