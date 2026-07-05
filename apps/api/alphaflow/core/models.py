from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


Decision = Literal["ALLOW", "WATCH", "REJECT"]
Market = Literal["US", "HK", "GLOBAL"]


class RiskLimits(BaseModel):
    max_single_weight: float = 0.2
    max_portfolio_drawdown: float = 0.15
    drawdown_de_risk: float = 0.1
    stop_loss: float = 0.08
    cash_buffer: float = 0.1
    max_turnover_per_rebalance: float = 0.4
    min_trades: int = 10
    min_sharpe: float = 0.5


class AgentRunRequest(BaseModel):
    query: str = Field(..., min_length=2)
    news_text: str | None = None
    strategy_id: str | None = None
    symbols: list[str] | None = None
    market: Market | None = None
    benchmark: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    initial_cash: float = 100_000
    max_drawdown: float | None = None
    risk_preference: Literal["low", "medium", "high"] = "medium"
    custom_weights: dict[str, float] | None = None


class StrategySpec(BaseModel):
    strategy_id: str
    strategy_name: str
    market: Market = "US"
    theme: str = "AI infrastructure"
    universe: list[str]
    benchmark: str = "QQQ"
    start_date: date
    end_date: date
    initial_cash: float = 100_000
    rebalance_frequency: Literal["weekly", "monthly"] = "weekly"
    top_n: int = 5
    risk_limits: RiskLimits = Field(default_factory=RiskLimits)
    custom_weights: dict[str, float] | None = None
    news_text: str | None = None
    source: Literal["doubao", "rules", "user"] = "rules"


class StrategyTemplate(BaseModel):
    id: str
    name: str
    category: str
    description: str
    market: Market = "GLOBAL"
    default_universe_key: str
    benchmark: str
    factor_weights: dict[str, float]
    min_trend_filter: str | None = "trend_ma60"
    top_n: int = 5
    source_inspiration: str


class AgentStep(BaseModel):
    label: str
    agent: str
    status: Literal["done", "running", "skipped", "warn"] = "done"
    detail: str


class MetricSummary(BaseModel):
    total_return: float
    annual_return: float
    benchmark_return: float
    excess_return: float
    max_drawdown: float
    annual_volatility: float
    sharpe_ratio: float
    calmar_ratio: float
    win_rate: float
    profit_loss_ratio: float
    turnover: float
    number_of_trades: int
    best_trade: float
    worst_trade: float


class RiskVerdict(BaseModel):
    allow_trade: bool
    decision: Decision
    reasons: list[str]
    suggested_action: str
    checks: list[dict[str, Any]]


class OrderPreview(BaseModel):
    symbol: str
    side: Literal["BUY", "SELL", "HOLD"]
    target_weight: float
    estimated_price: float
    estimated_quantity: int
    estimated_notional: float
    stop_loss: float
    reason: str


class AgentRunResponse(BaseModel):
    run_id: str
    generated_at: str
    steps: list[AgentStep]
    strategy_spec: StrategySpec
    templates: list[StrategyTemplate]
    data_source: str
    factor_rankings: list[dict[str, Any]]
    equity_curve: list[dict[str, Any]]
    drawdown_curve: list[dict[str, Any]]
    metrics: MetricSummary
    risk: RiskVerdict
    target_weights: dict[str, float]
    orders: list[OrderPreview]
    explanation: str
    news_items: list[dict[str, str]]
    qveris_status: dict[str, Any]


class ConfirmOrdersRequest(BaseModel):
    run_id: str
    orders: list[OrderPreview]
    strategy_spec: StrategySpec
    metrics: MetricSummary
    risk: RiskVerdict


class IndustryCompany(BaseModel):
    symbol: str
    name: str
    market: Market
    layer: str
    category: str
    role: str
    market_cap_usd_bn: float
    pe: float | None = None
    ps: float | None = None
    peg: float | None = None
    revenue_growth: float | None = None
    gross_margin: float | None = None
    valuation_signal: Literal["cheap", "fair", "expensive", "watch"] = "watch"
    evidence_strength: Literal["strong", "medium", "weak"] = "medium"
    key_metric: str
    risk: str
    research_priority: float


class IndustryLayer(BaseModel):
    id: str
    name: str
    direction: Literal["upstream", "midstream", "downstream", "infrastructure"]
    bottleneck_score: float
    why_it_matters: str
    key_metrics: list[str]


class IndustryChainResponse(BaseModel):
    theme: Literal["ai", "robotics"]
    title: str
    summary: str
    scarce_layers: list[str]
    layers: list[IndustryLayer]
    companies: list[IndustryCompany]
    valuation_columns: list[str]
    methodology: str
    disclaimer: str
