export type StrategyTemplate = {
  id: string;
  name: string;
  category: string;
  description: string;
  benchmark: string;
  default_universe_key: string;
  top_n: number;
};

export type AgentStep = {
  label: string;
  agent: string;
  status: "done" | "running" | "skipped" | "warn";
  detail: string;
};

export type StrategySpec = {
  strategy_id: string;
  strategy_name: string;
  market: "US" | "HK" | "GLOBAL";
  theme: string;
  universe: string[];
  benchmark: string;
  start_date: string;
  end_date: string;
  initial_cash: number;
  top_n: number;
  risk_limits: {
    max_single_weight: number;
    max_portfolio_drawdown: number;
    stop_loss: number;
    cash_buffer: number;
  };
};

export type Metrics = {
  total_return: number;
  annual_return: number;
  benchmark_return: number;
  excess_return: number;
  max_drawdown: number;
  annual_volatility: number;
  sharpe_ratio: number;
  calmar_ratio: number;
  win_rate: number;
  turnover: number;
  number_of_trades: number;
};

export type RiskVerdict = {
  allow_trade: boolean;
  decision: "ALLOW" | "WATCH" | "REJECT";
  reasons: string[];
  suggested_action: string;
  checks: Array<{ name: string; passed: boolean; value: number; limit: number; severity: string }>;
};

export type OrderPreview = {
  symbol: string;
  side: "BUY" | "SELL" | "HOLD";
  target_weight: number;
  estimated_price: number;
  estimated_quantity: number;
  estimated_notional: number;
  stop_loss: number;
  reason: string;
};

export type AgentRunResponse = {
  run_id: string;
  generated_at: string;
  steps: AgentStep[];
  strategy_spec: StrategySpec;
  templates: StrategyTemplate[];
  data_source: string;
  factor_rankings: Array<Record<string, number | string>>;
  equity_curve: Array<{ date: string; value: number }>;
  drawdown_curve: Array<{ date: string; drawdown: number }>;
  metrics: Metrics;
  risk: RiskVerdict;
  target_weights: Record<string, number>;
  orders: OrderPreview[];
  explanation: string;
  news_items: Array<{ title: string; source: string; summary: string }>;
  qveris_status: Record<string, unknown>;
};

export type Language = "zh" | "en";

export type SystemStatus = {
  volc_ark: {
    configured: boolean;
    model: string;
    base_url: string;
  };
  qveris: Record<string, unknown>;
  paper_trading_only: boolean;
  backtest_engine: string;
};

export type DataSourceConfig = {
  id: string;
  target: string;
  recommended_combo: string;
  reason: string;
  risk: string;
  enabled: boolean;
  providers: string[];
};

export type SystemConfig = {
  volc_ark: {
    api_key: string;
    api_key_masked: string;
    configured: boolean;
    model: string;
    base_url: string;
  };
  qveris: {
    api_key: string;
    api_key_masked: string;
    configured: boolean;
    base_url: string;
  };
  data_sources: DataSourceConfig[];
};

export type IndustryLayer = {
  id: string;
  name: string;
  direction: "upstream" | "midstream" | "downstream" | "infrastructure";
  bottleneck_score: number;
  why_it_matters: string;
  key_metrics: string[];
};

export type IndustryCompany = {
  symbol: string;
  name: string;
  market: "US" | "HK" | "GLOBAL";
  layer: string;
  category: string;
  role: string;
  market_cap_usd_bn: number;
  pe: number | null;
  ps: number | null;
  peg: number | null;
  revenue_growth: number | null;
  gross_margin: number | null;
  valuation_signal: "cheap" | "fair" | "expensive" | "watch";
  evidence_strength: "strong" | "medium" | "weak";
  key_metric: string;
  risk: string;
  research_priority: number;
};

export type IndustryChainResponse = {
  theme: "ai" | "robotics";
  title: string;
  summary: string;
  scarce_layers: string[];
  layers: IndustryLayer[];
  companies: IndustryCompany[];
  valuation_columns: string[];
  methodology: string;
  disclaimer: string;
};
