from __future__ import annotations

import re
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any

from alphaflow.clients.qveris import QVerisClient
from alphaflow.clients.volc import VolcArkClient
from alphaflow.core.models import AgentRunRequest, AgentRunResponse, AgentStep, RiskLimits, StrategySpec
from alphaflow.data.universes import BENCHMARKS, UNIVERSES, infer_universe_key, normalize_symbols
from alphaflow.services.backtest import run_backtest
from alphaflow.services.data_provider import load_market_data
from alphaflow.services.factors import build_factor_panel
from alphaflow.services.news import HOT_NEWS
from alphaflow.services.risk import evaluate_risk
from alphaflow.services.strategies import STRATEGY_TEMPLATES, choose_template, get_template


STRATEGY_ALIASES = {
    "横截面多因子": "cross_sectional_multifactor",
    "ai 基建动量": "ai_infra_momentum",
    "ai基建动量": "ai_infra_momentum",
    "etf 动量轮动": "etf_momentum_rotation",
    "etf动量轮动": "etf_momentum_rotation",
    "双均线趋势": "dual_ma_trend",
    "rsi 均值回归": "rsi_mean_reversion",
    "rsi均值回归": "rsi_mean_reversion",
    "布林均值回归": "bollinger_reversion",
    "macd 趋势": "macd_trend_proxy",
    "20 日突破": "breakout_20d",
    "20日突破": "breakout_20d",
    "低波质量": "low_vol_quality",
    "质量动量": "fundamental_quality_momentum",
    "新闻事件动量": "news_event_momentum",
    "港股科技轮动": "hk_tech_rotation",
    "防御型市场状态切换": "defensive_regime_switch",
    "自定义因子组合": "custom_factor_blend",
}


def _parse_drawdown(query: str) -> float | None:
    match = re.search(r"最大回撤(?:阈值|不要超过|不超过|控制在|限制|小于|低于)?\s*(\d{1,2}(?:\.\d+)?)(?:\s*)%", query)
    if not match:
        match = re.search(r"(\d{1,2}(?:\.\d+)?)(?:\s*)%[^。；，,]*回撤", query)
    if match:
        value = float(match.group(1)) / 100
        if 0.03 <= value <= 0.8:
            return value
    for keyword, value in [("低回撤", 0.1), ("保守", 0.1), ("激进", 0.25), ("满仓", 0.15)]:
        if keyword in query:
            return value
    return None


def _strategy_id_from_query(query: str) -> str | None:
    text = query.lower()
    for alias, strategy_id in STRATEGY_ALIASES.items():
        if alias in text:
            return strategy_id
    for template in STRATEGY_TEMPLATES:
        if template.name.lower() in text or template.id.lower() in text:
            return template.id
    return None


def _infer_market(query: str, llm_json: dict[str, Any] | None, request_market: str | None) -> str:
    if request_market:
        return request_market
    if llm_json and llm_json.get("market") in {"US", "HK", "GLOBAL"}:
        return llm_json["market"]
    text = query.lower()
    if "港" in query or ".hk" in text:
        return "HK"
    if "global" in text or "全球" in query:
        return "GLOBAL"
    return "US"


def _infer_strategy_id(query: str, llm_json: dict[str, Any] | None, explicit: str | None) -> str:
    query_strategy = _strategy_id_from_query(query)
    if query_strategy:
        return query_strategy
    if explicit:
        return explicit
    if llm_json and llm_json.get("strategy_hint"):
        candidate = str(llm_json["strategy_hint"])
        try:
            return get_template(candidate).id
        except Exception:
            pass
    return choose_template(query).id


def _default_dates(request: AgentRunRequest) -> tuple[date, date]:
    end = request.end_date or date.today()
    start = request.start_date or (end - timedelta(days=365 * 3 + 20))
    return start, end


def _parse_date_range(query: str) -> tuple[date | None, date | None]:
    matches = re.findall(r"\d{4}-\d{2}-\d{2}", query)
    if len(matches) < 2:
        return None, None
    try:
        return date.fromisoformat(matches[0]), date.fromisoformat(matches[1])
    except ValueError:
        return None, None


def _parse_initial_cash(query: str) -> float | None:
    match = re.search(r"初始资金\s*([0-9,]+(?:\.\d+)?)\s*(万)?", query)
    if not match:
        return None
    value = float(match.group(1).replace(",", ""))
    if match.group(2):
        value *= 10_000
    return value if value >= 1_000 else None


async def build_strategy_spec(request: AgentRunRequest, volc: VolcArkClient | None = None) -> tuple[StrategySpec, list[AgentStep], dict[str, Any] | None]:
    llm_json = await volc.extract_strategy_json(request.query, request.news_text) if volc else None
    market = _infer_market(request.query, llm_json, request.market)
    strategy_id = _infer_strategy_id(request.query, llm_json, request.strategy_id)
    template = get_template(strategy_id)
    universe_key = infer_universe_key(request.query, market)
    if template.default_universe_key:
        universe_key = template.default_universe_key

    symbols = request.symbols or (llm_json or {}).get("symbols") or UNIVERSES[universe_key]
    universe = normalize_symbols(symbols)
    benchmark = request.benchmark or (llm_json or {}).get("benchmark") or template.benchmark or BENCHMARKS.get(market, "QQQ")
    if benchmark not in universe:
        universe.append(benchmark)

    parsed_start, parsed_end = _parse_date_range(request.query)
    default_start, default_end = _default_dates(request)
    start = parsed_start or default_start
    end = parsed_end or default_end
    parsed_cash = _parse_initial_cash(request.query)
    parsed_drawdown = _parse_drawdown(request.query)
    max_drawdown = parsed_drawdown or request.max_drawdown or (llm_json or {}).get("max_drawdown")
    risk_limits = RiskLimits(max_portfolio_drawdown=float(max_drawdown or 0.15))
    if "满仓" in request.query:
        risk_limits.max_single_weight = 0.2
        risk_limits.cash_buffer = 0.15

    custom_weights = request.custom_weights if strategy_id == "custom_factor_blend" else None
    spec = StrategySpec(
        strategy_id=strategy_id,
        strategy_name=template.name,
        market=market,  # type: ignore[arg-type]
        theme=(llm_json or {}).get("theme") or ("HK technology" if market == "HK" else "AI infrastructure"),
        universe=universe,
        benchmark=benchmark,
        start_date=start,
        end_date=end,
        initial_cash=parsed_cash or request.initial_cash,
        top_n=template.top_n,
        risk_limits=risk_limits,
        custom_weights=custom_weights,
        news_text=request.news_text,
        source="doubao" if llm_json else "rules",
    )
    steps = [
        AgentStep(
            label="Reading your question",
            agent="Intake Agent",
            detail=f"Parsed objective, market, risk limit, and backtest window {start.isoformat()} to {end.isoformat()}.",
        ),
        AgentStep(
            label="Checking the news",
            agent="Research Agent",
            status="done" if request.news_text else "skipped",
            detail="User-pasted news converted into event score." if request.news_text else "No user news pasted; using demo finance ticker tape only.",
        ),
        AgentStep(label="Searching prediction markets", agent="Research Agent", status="skipped", detail="Prediction-market connector is optional for this MVP."),
        AgentStep(label="Searching the web", agent="Tool Agent", status="running", detail="Preparing QVeris discovery query."),
        AgentStep(label="Checking social media", agent="Sentiment Agent", status="skipped", detail="Social signal is planned as a future connector, not used for trading decisions."),
        AgentStep(label="Reviewing the sources", agent="Risk Agent", detail="Data source quality, coverage, and fallback mode will be shown in the run result."),
        AgentStep(label="Writing your answer", agent="Portfolio Agent", detail="Strategy, backtest, risk verdict, weights, and simulated orders will be generated."),
    ]
    return spec, steps, llm_json


def _qveris_query(request: AgentRunRequest, spec: StrategySpec) -> str:
    symbols = ", ".join(spec.universe[:8])
    news_clause = " user-pasted event news" if request.news_text else ""
    return (
        f"{spec.market} stock market data, financial news, SEC/HKEX filings, fundamentals, "
        f"earnings calendar, and analyst estimate APIs for {spec.theme}; tickers: {symbols}.{news_clause}"
    )


def _replace_step(steps: list[AgentStep], replacement: AgentStep) -> None:
    for index, step in enumerate(steps):
        if step.label == replacement.label:
            steps[index] = replacement
            return
    steps.append(replacement)


async def _run_qveris_discovery(
    request: AgentRunRequest,
    spec: StrategySpec,
    qveris: QVerisClient,
) -> dict[str, Any]:
    status = await qveris.status()
    if not status.get("configured"):
        return {
            **status,
            "discovery": {
                "attempted": False,
                "results_count": 0,
                "message": "QVeris API key is not configured, so discovery was skipped.",
            },
        }

    query = _qveris_query(request, spec)
    discovery = await qveris.discover(query, limit=3)
    results = discovery.get("results") if isinstance(discovery.get("results"), list) else []
    return {
        **status,
        "discovery": {
            "attempted": True,
            "query": query,
            "mode": discovery.get("mode", status.get("mode")),
            "search_id": discovery.get("search_id"),
            "results_count": len(results),
            "results": results[:3],
            "message": discovery.get("message"),
        },
    }


def _qveris_step(qveris_status: dict[str, Any]) -> AgentStep:
    discovery = qveris_status.get("discovery") or {}
    if not qveris_status.get("configured"):
        return AgentStep(
            label="Searching the web",
            agent="Tool Agent",
            status="skipped",
            detail="QVeris key is not configured; skipped discovery and continued with configured market data providers.",
        )
    if discovery.get("attempted") and discovery.get("results_count", 0) > 0:
        return AgentStep(
            label="Searching the web",
            agent="Tool Agent",
            status="done",
            detail=f"QVeris discovery returned {discovery.get('results_count')} candidate data tools via {discovery.get('mode') or 'configured adapter'}.",
        )
    return AgentStep(
        label="Searching the web",
        agent="Tool Agent",
        status="warn",
        detail=discovery.get("message") or "QVeris was configured, but discovery returned no usable results; configured market data providers were used.",
    )


async def run_agent(
    request: AgentRunRequest,
    cache_dir,
    volc: VolcArkClient | None,
    qveris: QVerisClient,
    data_sources: list[dict[str, Any]] | None = None,
) -> AgentRunResponse:
    run_id = f"run_{uuid.uuid4().hex[:10]}"
    spec, steps, _ = await build_strategy_spec(request, volc)
    qveris_status = await _run_qveris_discovery(request, spec, qveris)
    _replace_step(steps, _qveris_step(qveris_status))
    market_data = load_market_data(spec.universe, spec.start_date, spec.end_date, cache_dir, data_sources)
    factor_panel = build_factor_panel(market_data, spec.benchmark, spec.news_text)
    result = run_backtest(market_data, factor_panel, spec)
    risk = evaluate_risk(result.metrics, spec.risk_limits)
    explanation = _build_explanation(spec, result.metrics, risk, market_data.source)

    if market_data.warnings:
        steps.append(
            AgentStep(
                label="Data fallback",
                agent="Data Agent",
                status="warn",
                detail="; ".join(market_data.warnings[:3]),
            )
        )

    return AgentRunResponse(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        steps=steps,
        strategy_spec=spec,
        templates=STRATEGY_TEMPLATES,
        data_source=market_data.source,
        factor_rankings=result.factor_rankings,
        equity_curve=result.equity_curve,
        drawdown_curve=result.drawdown_curve,
        metrics=result.metrics,
        risk=risk,
        target_weights=result.target_weights,
        orders=[] if risk.decision == "REJECT" else result.orders,
        explanation=explanation,
        news_items=HOT_NEWS,
        qveris_status=qveris_status,
    )


def _build_explanation(spec: StrategySpec, metrics, risk, data_source: str) -> str:
    verdict = {"ALLOW": "可以进入用户确认环节", "WATCH": "可以小仓观察但需要严格风控", "REJECT": "不建议执行，风控已否决"}[risk.decision]
    return (
        f"结论：{verdict}。\n"
        f"策略使用 {spec.strategy_name}，市场为 {spec.market}，基准为 {spec.benchmark}，数据源为 {data_source}。\n"
        f"回测区间 {spec.start_date.isoformat()} 至 {spec.end_date.isoformat()}，初始资金 ${spec.initial_cash:,.0f}，"
        f"组合最大回撤阈值 {spec.risk_limits.max_portfolio_drawdown:.1%}。\n"
        f"回测由 vectorbt Portfolio.from_orders 执行。总收益 {metrics.total_return:.1%}，基准收益 {metrics.benchmark_return:.1%}，"
        f"最大回撤 {abs(metrics.max_drawdown):.1%}，夏普 {metrics.sharpe_ratio:.2f}。\n"
        "组合由所选策略模板的候选股票池、因子权重、调仓规则与风险规则生成；LLM 只负责理解用户意图和解释结果。"
    )
