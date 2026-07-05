from __future__ import annotations

from alphaflow.core.models import StrategyTemplate


STRATEGY_TEMPLATES: list[StrategyTemplate] = [
    StrategyTemplate(
        id="cross_sectional_multifactor",
        name="Cross-sectional Multi-factor",
        category="Core",
        description="Rank stocks by momentum, trend, relative strength, volatility, drawdown, and fundamentals.",
        default_universe_key="ai_chips_cloud_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={
            "momentum_60d": 0.22,
            "momentum_20d": 0.14,
            "trend_ma60": 0.16,
            "relative_strength": 0.16,
            "fundamental_quality": 0.12,
            "fundamental_growth": 0.08,
            "volatility_20d": -0.06,
            "drawdown_60d": -0.06,
        },
        source_inspiration="vectorbt/backtesting.py style factor ranking",
    ),
    StrategyTemplate(
        id="ai_infra_momentum",
        name="AI Infra Momentum",
        category="Theme",
        description="AI chips, cloud, networking, memory, and foundry momentum with quality score.",
        default_universe_key="ai_chips_cloud_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={
            "momentum_120d": 0.2,
            "momentum_60d": 0.2,
            "trend_ma60": 0.16,
            "volume_strength_20d": 0.08,
            "fundamental_quality": 0.12,
            "fundamental_growth": 0.12,
            "relative_strength": 0.12,
        },
        source_inspiration="open-source momentum rotation recipes",
    ),
    StrategyTemplate(
        id="etf_momentum_rotation",
        name="ETF Momentum Rotation",
        category="ETF",
        description="Rotate among broad equity, technology, semiconductor, bonds, and gold ETFs.",
        default_universe_key="etf_rotation",
        benchmark="SPY",
        top_n=3,
        factor_weights={"momentum_120d": 0.35, "momentum_60d": 0.2, "trend_ma120": 0.2, "volatility_20d": -0.15, "drawdown_60d": -0.1},
        source_inspiration="classic dual momentum ETF rotation",
    ),
    StrategyTemplate(
        id="dual_ma_trend",
        name="Dual MA Trend",
        category="Trend",
        description="Prefer assets above MA60 and MA120 with improving 20/60 day momentum.",
        default_universe_key="mega_cap_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={"trend_ma60": 0.28, "trend_ma120": 0.22, "momentum_20d": 0.15, "momentum_60d": 0.15, "relative_strength": 0.12, "volatility_20d": -0.08},
        source_inspiration="backtrader moving-average crossover examples",
    ),
    StrategyTemplate(
        id="rsi_mean_reversion",
        name="RSI Mean Reversion",
        category="Mean Reversion",
        description="Buy high-quality assets with temporary RSI weakness while longer trend stays positive.",
        default_universe_key="mega_cap_us",
        benchmark="QQQ",
        top_n=4,
        factor_weights={"rsi_14": -0.28, "trend_ma120": 0.2, "fundamental_quality": 0.18, "momentum_60d": 0.12, "drawdown_60d": -0.12, "volatility_20d": -0.1},
        source_inspiration="backtesting.py RSI examples",
    ),
    StrategyTemplate(
        id="bollinger_reversion",
        name="Bollinger-style Reversion",
        category="Mean Reversion",
        description="Use drawdown and short-term weakness as a reversion setup, filtered by quality and trend.",
        default_universe_key="mega_cap_us",
        benchmark="QQQ",
        top_n=4,
        factor_weights={"drawdown_60d": -0.26, "rsi_14": -0.16, "trend_ma120": 0.18, "fundamental_quality": 0.18, "volatility_20d": -0.12, "relative_strength": 0.1},
        source_inspiration="open-source Bollinger-band mean reversion patterns",
    ),
    StrategyTemplate(
        id="macd_trend_proxy",
        name="MACD Trend Proxy",
        category="Trend",
        description="Approximate MACD behavior using 20/60 day momentum and trend acceleration.",
        default_universe_key="ai_chips_cloud_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={"momentum_20d": 0.28, "momentum_60d": 0.22, "trend_ma20": 0.14, "trend_ma60": 0.14, "volume_strength_20d": 0.1, "volatility_20d": -0.12},
        source_inspiration="TA-Lib MACD strategy examples",
    ),
    StrategyTemplate(
        id="breakout_20d",
        name="20D Breakout",
        category="Breakout",
        description="Prefer assets pressing against 20-day highs with strong volume and relative strength.",
        default_universe_key="ai_chips_cloud_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={"breakout_20d": 0.24, "volume_strength_20d": 0.2, "relative_strength": 0.2, "momentum_20d": 0.16, "fundamental_growth": 0.1, "volatility_20d": -0.1},
        source_inspiration="Donchian breakout strategy family",
    ),
    StrategyTemplate(
        id="low_vol_quality",
        name="Low Vol Quality",
        category="Risk Control",
        description="Rank for quality, cash flow, lower realized volatility, and smaller drawdowns.",
        default_universe_key="mega_cap_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={"fundamental_quality": 0.24, "fundamental_cashflow": 0.22, "fundamental_valuation": 0.12, "volatility_20d": -0.2, "drawdown_60d": -0.14, "trend_ma60": 0.08},
        source_inspiration="quality and low-volatility factor literature",
    ),
    StrategyTemplate(
        id="fundamental_quality_momentum",
        name="Quality + Momentum",
        category="Fundamental",
        description="Blend fundamental quality/growth/cashflow with 60/120 day momentum.",
        default_universe_key="ai_chips_cloud_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={"fundamental_quality": 0.2, "fundamental_growth": 0.18, "fundamental_cashflow": 0.14, "fundamental_valuation": 0.04, "momentum_120d": 0.18, "momentum_60d": 0.14, "relative_strength": 0.12},
        source_inspiration="Fama-French quality momentum extensions",
    ),
    StrategyTemplate(
        id="news_event_momentum",
        name="News Event Momentum",
        category="Event",
        description="Convert pasted news into an event score, then require price confirmation.",
        default_universe_key="ai_chips_cloud_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={"event_score": 0.28, "momentum_5d": 0.18, "momentum_20d": 0.18, "volume_strength_20d": 0.12, "relative_strength": 0.14, "volatility_20d": -0.1},
        source_inspiration="event-driven NLP strategy prototypes",
    ),
    StrategyTemplate(
        id="hk_tech_rotation",
        name="HK Tech Rotation",
        category="Hong Kong",
        description="Rotate among liquid Hong Kong technology leaders and the HK benchmark ETF.",
        market="HK",
        default_universe_key="hk_tech",
        benchmark="2800.HK",
        top_n=4,
        factor_weights={"momentum_60d": 0.22, "momentum_20d": 0.18, "relative_strength": 0.18, "trend_ma60": 0.16, "fundamental_quality": 0.12, "volatility_20d": -0.08, "drawdown_60d": -0.06},
        source_inspiration="sector rotation strategy family",
    ),
    StrategyTemplate(
        id="defensive_regime_switch",
        name="Defensive Regime Switch",
        category="Risk Control",
        description="Switch toward bonds, gold, utilities, health care, and cash-like ETFs when trend weakens.",
        default_universe_key="defensive_etf",
        benchmark="SPY",
        top_n=3,
        factor_weights={"trend_ma120": 0.24, "momentum_120d": 0.22, "volatility_20d": -0.22, "drawdown_60d": -0.18, "relative_strength": 0.14},
        source_inspiration="dual momentum plus defensive asset allocation",
    ),
    StrategyTemplate(
        id="custom_factor_blend",
        name="Custom Factor Blend",
        category="Custom",
        description="Let the user override factor weights while keeping the same strategy backtest and risk checks.",
        default_universe_key="ai_chips_cloud_us",
        benchmark="QQQ",
        top_n=5,
        factor_weights={"momentum_60d": 0.2, "trend_ma60": 0.2, "relative_strength": 0.2, "fundamental_quality": 0.2, "volatility_20d": -0.2},
        source_inspiration="user-defined strategy registry",
    ),
]


def get_template(strategy_id: str | None) -> StrategyTemplate:
    if strategy_id:
        for template in STRATEGY_TEMPLATES:
            if template.id == strategy_id:
                return template
    return STRATEGY_TEMPLATES[0]


def choose_template(query: str, explicit: str | None = None) -> StrategyTemplate:
    if explicit:
        return get_template(explicit)
    text = query.lower()
    if "港" in query or ".hk" in text:
        return get_template("hk_tech_rotation")
    if "etf" in text or "轮动" in query:
        return get_template("etf_momentum_rotation")
    if "新闻" in query or "发布" in query or "event" in text:
        return get_template("news_event_momentum")
    if "满仓" in query or "最近涨得最强" in query:
        return get_template("breakout_20d")
    if "防御" in query or "低回撤" in query:
        return get_template("defensive_regime_switch")
    if "基本面" in query or "quality" in text:
        return get_template("fundamental_quality_momentum")
    return get_template("ai_infra_momentum" if ("ai" in text or "芯片" in query) else "cross_sectional_multifactor")
