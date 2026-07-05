"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import Link from "next/link";
import {
  BarChart3,
  Bot,
  CheckCircle2,
  Clock3,
  Cpu,
  Database,
  Home,
  Languages,
  Layers3,
  Library,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  Search,
  SendHorizontal,
  Settings,
  ShieldAlert,
  ShieldCheck,
  SlidersHorizontal,
  TrendingUp,
  WalletCards
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { confirmOrders, fetchHotNews, fetchIndustryChain, fetchSystemConfig, fetchSystemStatus, fetchTemplates, runAgent, saveSystemConfig } from "@/lib/api";
import type { AgentRunResponse, DataSourceConfig, IndustryChainResponse, Language, StrategyTemplate, SystemConfig, SystemStatus } from "@/lib/types";

const DEFAULT_QUERY = "";

type RecentItem = {
  title: string;
  detail: string;
  query: string;
  strategyId: string;
};

const RECENT_PROMPTS: RecentItem[] = [
  {
    title: "AI Capex 供应链",
    detail: "NVDA / AVGO / TSM",
    query: "围绕 AI capex、先进封装、HBM 和数据中心电力，生成一个美股多因子交易策略。",
    strategyId: "ai_infra_momentum"
  },
  {
    title: "港股科技轮动",
    detail: "700.HK / 9988.HK / 3690.HK",
    query: "我想做一个港股科技股轮动组合，最大回撤不要超过 18%，跑赢 2800.HK。",
    strategyId: "hk_tech_rotation"
  },
  {
    title: "事件驱动观察",
    detail: "财报 / 政策 / 订单",
    query: "基于最新财经事件，筛选适合小仓观察的事件驱动组合，并给出风控条件。",
    strategyId: "news_event_momentum"
  }
];

const FALLBACK_NEWS = [
  {
    title: "AI 基建订单继续扩张",
    source: "StratPilot",
    summary: "大型云厂商继续提高 AI 服务器、网络和电力基础设施预算，先进封装、HBM、交换芯片和散热链条值得跟踪。"
  },
  {
    title: "机器人产业链进入催化窗口",
    source: "StratPilot",
    summary: "人形机器人和工业自动化主题升温，伺服、电机、减速器、传感器和控制器成为优先验证层级。"
  },
  {
    title: "港股互联网估值修复",
    source: "StratPilot",
    summary: "南向资金、回购、盈利修复与 AI 应用投入共同影响港股科技权重股，可用趋势和回撤约束做轮动。"
  }
];

const COPY = {
  zh: {
    subtitle: "AI 交易策略工作台",
    trading: "工作台",
    research: "策略中心",
    settings: "系统设置",
    portfolio: "组合",
    recent: "Recent",
    createTitle: "你今天有什么策略？",
    promptPlaceholder: "你今天有什么策略？",
    generate: "生成",
    running: "运行中",
    runProgress: "运行进度",
    progressRead: "解析策略请求、日期、资金和风控阈值",
    progressData: "检查本地缓存，缺失 ticker 时调用在线行情并写入缓存",
    progressStrategy: "按策略模板生成股票池、因子权重和调仓规则",
    progressBacktest: "用 vectorbt 执行回测，计算净值、交易和回撤。",
    progressRisk: "核对最大回撤、夏普、交易样本、基准和波动率。",
    progressWriting: "整理风控日志、组合权重和解释。",
    progressIntakeLabel: "解析",
    progressDataLabel: "数据",
    progressStrategyLabel: "策略",
    progressBacktestLabel: "回测",
    progressRiskLabel: "风控",
    progressReportLabel: "报告",
    recommendations: "热点推荐",
    community: "策略灵感",
    advanced: "参数",
    strategyTemplate: "策略",
    presetStrategies: "预制策略",
    backtestPeriod: "回测区间",
    start: "开始日期",
    end: "结束日期",
    cash: "初始资金",
    maxDD: "最大回撤 %",
    newsInput: "新闻输入",
    newsPlaceholder: "粘贴新闻、公告或财报摘要，事件因子会进入打分。",
    heroEyebrow: "Human-in-the-loop 交易 Agent",
    heroTitle: "运行策略后生成交易方案",
    totalReturn: "总收益",
    benchmark: "基准",
    maxDrawdown: "最大回撤",
    sharpe: "夏普",
    trades: "交易次数",
    data: "数据源",
    equity: "回测净值",
    drawdown: "回撤",
    riskVerdict: "风控结论",
    riskLog: "风控日志",
    actual: "实际值",
    limit: "阈值",
    status: "状态",
    passed: "通过",
    hardFail: "硬失败",
    warning: "警告",
    suggestedAction: "建议动作",
    allow: "通过",
    reject: "拒绝",
    buy: "买入",
    sell: "卖出",
    hold: "持有",
    symbol: "标的",
    score: "评分",
    growth: "增长",
    grossMargin: "毛利率",
    trend: "趋势",
    quality: "质量",
    event: "事件",
    cashLabel: "现金",
    templateCount: "个策略",
    topN: "前",
    notLoaded: "未加载",
    enforced: "已启用",
    restReady: "QVeris 已接入",
    restPending: "REST 待配置",
    disabled: "未启用",
    upstream: "上游",
    midstream: "中游",
    downstream: "下游",
    infrastructure: "基础设施",
    cheap: "低估",
    fair: "合理",
    expensive: "偏贵",
    watch: "观察",
    strong: "强",
    medium: "中",
    weak: "弱",
    factorRankings: "因子排名",
    portfolioWeights: "建议仓位",
    orderPreview: "模拟订单",
    confirm: "确认模拟订单",
    rejected: "风控已拒绝生成模拟订单。",
    noRanking: "暂无排名。",
    emptyRisk: "运行策略后查看通过 / 观察 / 拒绝。",
    industryTitle: "AI 与机器人产业链研究",
    industrySubtitle: "先排产业链层级，再看公司估值与证据强度。",
    aiChain: "AI 基础设施",
    roboticsChain: "机器人",
    scarceLayers: "优先关注的卡点",
    valueChain: "上下游层级",
    valuationTable: "估值参考",
    methodology: "研究口径",
    marketCap: "市值",
    category: "分类",
    role: "产业链位置",
    priority: "优先级",
    evidence: "证据",
    keyMetric: "主指标",
    risk: "风险",
    systemSettings: "系统设置",
    language: "语言",
    dataMode: "数据模式",
    modelProvider: "模型服务",
    volcProvider: "火山引擎大模型",
    apiKey: "API Key",
    configured: "已配置",
    notConfigured: "未配置",
    checking: "检查中",
    model: "模型",
    apiBase: "API 地址",
    qveris: "QVeris 数据发现",
    paperOnly: "仅模拟交易",
    deterministic: "策略回测与风控",
    sourcePolicy: "来源策略",
    dataSourcePortfolio: "数据源组合配置",
    target: "目标",
    recommendedCombo: "推荐组合",
    providers: "来源",
    reason: "原因",
    riskPoint: "风险点",
    enabled: "启用",
    saveSettings: "保存设置",
    savingSettings: "保存中",
    settingsSaved: "设置已保存",
    saved: "模拟订单已确认并写入 paper trading ledger。"
  },
  en: {
    subtitle: "AI Trading Strategy Desk",
    trading: "Workbench",
    research: "Strategy Center",
    settings: "Settings",
    portfolio: "Portfolio",
    recent: "Recent",
    createTitle: "What strategy are you running today?",
    promptPlaceholder: "What strategy are you running today?",
    generate: "Generate",
    running: "Running",
    runProgress: "Run Progress",
    progressRead: "Parsing strategy request, dates, cash, and risk limit.",
    progressData: "Checking cache; missing tickers use online prices and then write cache.",
    progressStrategy: "Building universe, factor weights, and rebalance rules from the template.",
    progressBacktest: "Running vectorbt backtest for equity, trades, and drawdown.",
    progressRisk: "Checking drawdown, Sharpe, trade sample, benchmark, and volatility.",
    progressWriting: "Preparing risk log, weights, and explanation.",
    progressIntakeLabel: "Intake",
    progressDataLabel: "Data",
    progressStrategyLabel: "Strategy",
    progressBacktestLabel: "Backtest",
    progressRiskLabel: "Risk",
    progressReportLabel: "Report",
    recommendations: "Hot Ideas",
    community: "Strategy Ideas",
    advanced: "Controls",
    strategyTemplate: "Strategy",
    presetStrategies: "Preset Strategies",
    backtestPeriod: "Backtest Period",
    start: "Start",
    end: "End",
    cash: "Cash",
    maxDD: "Max DD %",
    newsInput: "News Input",
    newsPlaceholder: "Paste news, filings, or earnings notes. Event score will enter factor ranking.",
    heroEyebrow: "Human-in-the-loop Trading Agent",
    heroTitle: "Run a strategy to generate the trading plan",
    totalReturn: "Total Return",
    benchmark: "Benchmark",
    maxDrawdown: "Max Drawdown",
    sharpe: "Sharpe",
    trades: "Trades",
    data: "Data",
    equity: "Backtest Equity",
    drawdown: "Drawdown",
    riskVerdict: "Risk Verdict",
    riskLog: "Risk Log",
    actual: "Actual",
    limit: "Limit",
    status: "Status",
    passed: "Pass",
    hardFail: "Hard Fail",
    warning: "Warn",
    suggestedAction: "Suggested Action",
    allow: "Allow",
    reject: "Reject",
    buy: "Buy",
    sell: "Sell",
    hold: "Hold",
    symbol: "Symbol",
    score: "Score",
    growth: "Growth",
    grossMargin: "GM",
    trend: "Trend",
    quality: "Quality",
    event: "Event",
    cashLabel: "Cash",
    templateCount: "templates",
    topN: "Top",
    notLoaded: "not loaded",
    enforced: "enforced",
    restReady: "QVeris REST",
    restPending: "REST pending",
    disabled: "off",
    upstream: "Upstream",
    midstream: "Midstream",
    downstream: "Downstream",
    infrastructure: "Infrastructure",
    cheap: "Cheap",
    fair: "Fair",
    expensive: "Expensive",
    watch: "Watch",
    strong: "Strong",
    medium: "Medium",
    weak: "Weak",
    factorRankings: "Factor Rankings",
    portfolioWeights: "Portfolio Weights",
    orderPreview: "Order Preview",
    confirm: "Confirm Paper Orders",
    rejected: "Risk verdict rejected the simulated order.",
    noRanking: "No ranking yet.",
    emptyRisk: "Run the agent to see ALLOW / WATCH / REJECT.",
    industryTitle: "AI and Robotics Value-chain Research",
    industrySubtitle: "Rank scarce layers first, then compare valuation and evidence strength.",
    aiChain: "AI Infrastructure",
    roboticsChain: "Robotics",
    scarceLayers: "Scarce Layers",
    valueChain: "Value-chain Layers",
    valuationTable: "Valuation Reference",
    methodology: "Methodology",
    marketCap: "Market Cap",
    category: "Category",
    role: "Value-chain Role",
    priority: "Priority",
    evidence: "Evidence",
    keyMetric: "Key Metric",
    risk: "Risk",
    systemSettings: "System Settings",
    language: "Language",
    dataMode: "Data Mode",
    modelProvider: "Model Provider",
    volcProvider: "Volcengine Ark",
    apiKey: "API Key",
    configured: "Configured",
    notConfigured: "Not configured",
    checking: "Checking",
    model: "Model",
    apiBase: "API Base",
    qveris: "QVeris Discovery",
    paperOnly: "Paper Trading Only",
    deterministic: "Strategy Backtest and Risk",
    sourcePolicy: "Source Policy",
    dataSourcePortfolio: "Data Source Portfolio",
    target: "Goal",
    recommendedCombo: "Recommended Stack",
    providers: "Providers",
    reason: "Reason",
    riskPoint: "Risks",
    enabled: "Enabled",
    saveSettings: "Save Settings",
    savingSettings: "Saving",
    settingsSaved: "Settings saved",
    saved: "Paper orders confirmed and written to the ledger."
  }
} satisfies Record<Language, Record<string, string>>;

function pct(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

function money(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

function bn(value: number) {
  return `$${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}B`;
}

function ratio(value: number | null) {
  return value === null ? "-" : value.toFixed(value >= 10 ? 0 : 1);
}

function dateInputValue(date: Date) {
  return date.toISOString().slice(0, 10);
}

function defaultBacktestEnd() {
  return dateInputValue(new Date());
}

function defaultBacktestStart() {
  const date = new Date();
  date.setFullYear(date.getFullYear() - 3);
  return dateInputValue(date);
}

function splitProviders(value: string) {
  return value.replace(/[，,/]/g, "+").split("+").map((item) => item.trim()).filter(Boolean);
}

function riskCheckLabel(name: string) {
  const labels: Record<string, string> = {
    "Max drawdown": "最大回撤",
    "Sharpe ratio": "夏普比率",
    "Trade sample": "交易样本",
    "Benchmark comparison": "跑赢基准",
    "Annual volatility": "年化波动"
  };
  return labels[name] ?? name;
}

function riskCheckValue(name: string, value: number) {
  if (name === "Sharpe ratio") return value.toFixed(2);
  if (name === "Trade sample") return String(Math.round(value));
  return pct(value);
}

function localizedToken(t: Record<string, string>, value: string) {
  return t[value] ?? value;
}

function decisionLabel(t: Record<string, string>, decision: "ALLOW" | "WATCH" | "REJECT") {
  const labels = {
    ALLOW: t.allow,
    WATCH: t.watch,
    REJECT: t.reject
  };
  return labels[decision];
}

function orderSideLabel(t: Record<string, string>, side: string) {
  const labels: Record<string, string> = {
    BUY: t.buy,
    SELL: t.sell,
    HOLD: t.hold
  };
  return labels[side] ?? side;
}

function riskStatusLabel(t: Record<string, string>, passed: boolean, severity: string) {
  if (passed) return t.passed;
  return severity === "hard" ? t.hardFail : t.warning;
}

function runProgressSteps(t: Record<string, string>, activeIndex: number) {
  const steps = [
    { label: t.progressIntakeLabel, detail: t.progressRead },
    { label: t.progressDataLabel, detail: t.progressData },
    { label: t.progressStrategyLabel, detail: t.progressStrategy },
    { label: t.progressBacktestLabel, detail: t.progressBacktest },
    { label: t.progressRiskLabel, detail: t.progressRisk },
    { label: t.progressReportLabel, detail: t.progressWriting }
  ];
  return steps.map((step, index) => ({
    ...step,
    status: index < activeIndex ? "done" : index === activeIndex ? "running" : "pending"
  }));
}

function verdictLabel(result: AgentRunResponse | null) {
  return result?.risk.decision ?? "WATCH";
}

function strategyDisplayName(template: StrategyTemplate) {
  const names: Record<string, string> = {
    cross_sectional_multifactor: "横截面多因子",
    ai_infra_momentum: "AI 基建动量",
    etf_momentum_rotation: "ETF 动量轮动",
    dual_ma_trend: "双均线趋势",
    rsi_mean_reversion: "RSI 均值回归",
    breakout_20d: "20 日突破",
    defensive_regime_switch: "防御型市场状态切换",
    hk_tech_rotation: "港股科技轮动",
    news_event_momentum: "新闻事件动量",
    quality_growth_compounder: "质量成长复合",
    low_volatility_income: "低波红利",
    semiconductor_supply_chain: "半导体供应链",
    robotics_value_chain: "机器人产业链",
    custom_factor_blend: "自定义因子组合"
  };
  return names[template.id] ?? template.name;
}

function strategySummary(template: StrategyTemplate) {
  const summaries: Record<string, string> = {
    cross_sectional_multifactor: "动量、趋势、相对强弱、波动率与基本面综合打分。",
    ai_infra_momentum: "AI 芯片、云、网络、存储与晶圆代工动量质量组合。",
    etf_momentum_rotation: "宽基、科技、半导体、债券与黄金 ETF 动量轮动。",
    dual_ma_trend: "用 MA60/MA120 趋势过滤并叠加 20/60 日动量。",
    rsi_mean_reversion: "长期趋势向上时，捕捉短期 RSI 弱势修复。",
    bollinger_reversion: "用回撤与短期弱势寻找质量资产的均值回归机会。",
    macd_trend_proxy: "用 20/60 日动量和趋势加速度近似 MACD 趋势。",
    breakout_20d: "筛选接近 20 日新高且量能增强的突破资产。",
    low_vol_quality: "质量、现金流、低波动与小回撤优先。",
    fundamental_quality_momentum: "基本面质量、成长、现金流与中期动量结合。",
    news_event_momentum: "把新闻事件转为事件分，再要求价格确认。",
    hk_tech_rotation: "港股科技龙头轮动，兼顾趋势、相对强弱和波动。",
    defensive_regime_switch: "趋势转弱时切向债券、黄金、防御 ETF。",
    custom_factor_blend: "用户自定义因子权重，保留确定性回测和风控。"
  };
  return summaries[template.id] ?? template.description;
}

function presetQueryPrefix(template: StrategyTemplate) {
  return `回测「${strategyDisplayName(template)}」预制策略`;
}

function buildPresetQuery(template: StrategyTemplate, startDate: string, endDate: string, initialCash: number, maxDrawdown: number) {
  return `${presetQueryPrefix(template)}，区间 ${startDate} 至 ${endDate}，初始资金 ${initialCash} 美元，最大回撤阈值 ${maxDrawdown}%，查看收益、最大回撤和风控结果。`;
}

function parsePromptParams(text: string, templates: StrategyTemplate[]) {
  const dates = text.match(/\d{4}-\d{2}-\d{2}/g) ?? [];
  const cashMatch = text.match(/初始资金\s*([0-9,]+(?:\.\d+)?)\s*(万)?/);
  const drawdownMatch =
    text.match(/最大回撤(?:阈值|不要超过|不超过|控制在|限制|小于|低于)?\s*([0-9]+(?:\.\d+)?)\s*%/) ??
    text.match(/([0-9]+(?:\.\d+)?)\s*%[^。；，,]*回撤/);
  const matchedTemplate = templates.find((template) => {
    const displayName = strategyDisplayName(template).toLowerCase();
    const englishName = template.name.toLowerCase();
    const id = template.id.toLowerCase();
    const lowered = text.toLowerCase();
    return lowered.includes(displayName) || lowered.includes(englishName) || lowered.includes(id);
  });
  const initialCash = cashMatch ? Number(cashMatch[1].replace(/,/g, "")) * (cashMatch[2] ? 10000 : 1) : undefined;
  const maxDrawdown = drawdownMatch ? Number(drawdownMatch[1]) : undefined;
  return {
    strategyId: matchedTemplate?.id,
    startDate: dates[0],
    endDate: dates[1],
    initialCash: initialCash && initialCash >= 1000 ? initialCash : undefined,
    maxDrawdown: maxDrawdown && maxDrawdown >= 1 && maxDrawdown <= 80 ? maxDrawdown : undefined
  };
}

export default function StratPilotShell({ initialView = "trading" }: { initialView?: "trading" | "research" | "settings" }) {
  const [language, setLanguage] = useState<Language>("zh");
  const t = COPY[language];
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeView, setActiveView] = useState<"trading" | "research" | "settings">(initialView);
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [newsText, setNewsText] = useState("");
  const [strategyId, setStrategyId] = useState("ai_infra_momentum");
  const [startDate, setStartDate] = useState(defaultBacktestStart);
  const [endDate, setEndDate] = useState(defaultBacktestEnd);
  const [initialCash, setInitialCash] = useState(100000);
  const [maxDrawdown, setMaxDrawdown] = useState(15);
  const [templates, setTemplates] = useState<StrategyTemplate[]>([]);
  const [hotNews, setHotNews] = useState<Array<{ title: string; source: string; summary: string }>>([]);
  const [recentHistory, setRecentHistory] = useState<RecentItem[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [systemConfig, setSystemConfig] = useState<SystemConfig | null>(null);
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [industryTheme, setIndustryTheme] = useState<"ai" | "robotics">("ai");
  const [industry, setIndustry] = useState<IndustryChainResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [runningStepIndex, setRunningStepIndex] = useState(0);
  const [confirming, setConfirming] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  const [message, setMessage] = useState("");
  const [configMessage, setConfigMessage] = useState("");

  useEffect(() => {
    fetchTemplates().then(setTemplates).catch(() => undefined);
    fetchHotNews().then(setHotNews).catch(() => undefined);
    fetchSystemStatus().then(setSystemStatus).catch(() => undefined);
    fetchSystemConfig().then(setSystemConfig).catch(() => undefined);
  }, []);

  useEffect(() => {
    setActiveView(initialView);
  }, [initialView]);

  useEffect(() => {
    fetchIndustryChain(industryTheme, language).then(setIndustry).catch(() => undefined);
  }, [industryTheme, language]);

  useEffect(() => {
    if (!loading) return;
    setRunningStepIndex(0);
    const timer = window.setInterval(() => {
      setRunningStepIndex((current) => Math.min(current + 1, 5));
    }, 3500);
    return () => window.clearInterval(timer);
  }, [loading]);

  const chartData = useMemo(() => {
    if (!result) return [];
    const drawdownByDate = new Map(result.drawdown_curve.map((row) => [row.date, row.drawdown]));
    return result.equity_curve.map((row) => ({
      date: row.date.slice(5),
      value: row.value,
      drawdown: drawdownByDate.get(row.date) ?? 0
    }));
  }, [result]);

  const recommendationCards = useMemo(() => {
    const source = (hotNews.length ? hotNews : FALLBACK_NEWS).slice(0, 3);
    const strategies = ["ai_infra_momentum", "news_event_momentum", "hk_tech_rotation", "cross_sectional_multifactor"];
    return source.map((item, index) => ({
      ...item,
      strategyId: strategies[index % strategies.length],
      signal: index % 3 === 0 ? "动量" : index % 3 === 1 ? "事件" : "产业链",
      query: `基于这条事件生成交易策略：${item.summary}`
    }));
  }, [hotNews]);

  const recentItems = useMemo(() => {
    const seen = new Set<string>();
    return [...recentHistory, ...RECENT_PROMPTS].filter((item) => {
      if (seen.has(item.strategyId)) return false;
      seen.add(item.strategyId);
      return true;
    }).slice(0, 6);
  }, [recentHistory]);

  function trackRecent(item: RecentItem) {
    setRecentHistory((current) => {
      const next = [item, ...current.filter((existing) => existing.strategyId !== item.strategyId)];
      return next.slice(0, 8);
    });
  }

  async function handleRun() {
    const effectiveQuery = query.trim() || "请根据当前热点新闻和事件，帮我发现一个值得研究的港美股投资机会，并生成可回测策略。";
    const promptParams = parsePromptParams(effectiveQuery, templates);
    const effectiveStrategyId = promptParams.strategyId ?? strategyId;
    const effectiveStartDate = promptParams.startDate ?? startDate;
    const effectiveEndDate = promptParams.endDate ?? endDate;
    const effectiveInitialCash = promptParams.initialCash ?? initialCash;
    const effectiveMaxDrawdown = promptParams.maxDrawdown ?? maxDrawdown;
    setLoading(true);
    setRunningStepIndex(0);
    setMessage("");
    try {
      setQuery(effectiveQuery);
      setStrategyId(effectiveStrategyId);
      setStartDate(effectiveStartDate);
      setEndDate(effectiveEndDate);
      setInitialCash(effectiveInitialCash);
      setMaxDrawdown(effectiveMaxDrawdown);
      const data = await runAgent({
        query: effectiveQuery,
        strategy_id: effectiveStrategyId || undefined,
        news_text: newsText || undefined,
        start_date: effectiveStartDate || undefined,
        end_date: effectiveEndDate || undefined,
        initial_cash: effectiveInitialCash,
        max_drawdown: effectiveMaxDrawdown / 100
      });
      setResult(data);
      setStrategyId(data.strategy_spec.strategy_id);
      setStartDate(data.strategy_spec.start_date);
      setEndDate(data.strategy_spec.end_date);
      setInitialCash(data.strategy_spec.initial_cash);
      setMaxDrawdown(Math.round(data.strategy_spec.risk_limits.max_portfolio_drawdown * 100));
      const completedTemplate = data.templates.find((template) => template.id === data.strategy_spec.strategy_id);
      trackRecent({
        title: completedTemplate ? strategyDisplayName(completedTemplate) : data.strategy_spec.strategy_name,
        detail: `${data.strategy_spec.start_date} - ${data.strategy_spec.end_date} / ${pct(data.metrics.total_return)}`,
        query: effectiveQuery,
        strategyId: data.strategy_spec.strategy_id
      });
      setActiveView("trading");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Agent run failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm() {
    if (!result || result.orders.length === 0) return;
    setConfirming(true);
    setMessage("");
    try {
      await confirmOrders({
        run_id: result.run_id,
        orders: result.orders,
        strategy_spec: result.strategy_spec,
        metrics: result.metrics,
        risk: result.risk
      });
      setMessage(t.saved);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Confirm failed");
    } finally {
      setConfirming(false);
    }
  }

  async function handleSaveSystemConfig(nextConfig: SystemConfig) {
    setSavingConfig(true);
    setConfigMessage("");
    try {
      const savedConfig = await saveSystemConfig(nextConfig);
      setSystemConfig(savedConfig);
      const latestStatus = await fetchSystemStatus();
      setSystemStatus(latestStatus);
      setConfigMessage(t.settingsSaved);
    } catch (error) {
      setConfigMessage(error instanceof Error ? error.message : "Save failed");
    } finally {
      setSavingConfig(false);
    }
  }

  function applyRecommendation(card: { title: string; query: string; summary: string; strategyId: string }) {
    setQuery(card.query);
    setNewsText(card.summary);
    setStrategyId(card.strategyId);
    trackRecent({ title: card.title, detail: "热点推荐", query: card.query, strategyId: card.strategyId });
    setActiveView("trading");
  }

  function applyRecent(item: RecentItem) {
    setQuery(item.query);
    setStrategyId(item.strategyId);
    trackRecent(item);
    setActiveView("trading");
  }

  const qverisConfigured = Boolean(systemStatus?.qveris.configured);

  return (
    <main className={sidebarOpen ? "appFrame" : "appFrame sidebarCollapsed"}>
      <aside className="rail">
        <div className="brandBadge">
          <div className="brandOrb">SP</div>
        </div>
        <button className="sidebarToggle" onClick={() => setSidebarOpen(!sidebarOpen)} title={sidebarOpen ? "收起边栏" : "展开边栏"}>
          {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeftOpen size={18} />}
        </button>

        <nav className="navStack" aria-label="Primary navigation">
          <Link className={activeView === "trading" ? "navItem active" : "navItem"} href="/workbench">
            <Home size={20} />
            <span>{t.trading}</span>
          </Link>
          <Link className={activeView === "research" ? "navItem active" : "navItem"} href="/strategies">
            <Library size={20} />
            <span>{t.research}</span>
          </Link>
          <Link className={activeView === "settings" ? "navItem active" : "navItem"} href="/settings">
            <Settings size={20} />
            <span>{t.settings}</span>
          </Link>
        </nav>

        <section className="recentRail">
          <div className="railTitle">
            <Clock3 size={15} />
            <span>{t.recent}</span>
          </div>
          <div className="recentList">
            {recentItems.map((item) => (
              <button key={`${item.title}-${item.detail}`} onClick={() => applyRecent(item)}>
                <span>{item.title}</span>
              </button>
            ))}
          </div>
        </section>

        <div className="railFooter">
          <button className="languageButton" onClick={() => setLanguage(language === "zh" ? "en" : "zh")} title={t.language}>
            <Languages size={17} />
            <span>{language === "zh" ? "中文" : "EN"}</span>
          </button>
          <div className={qverisConfigured ? "creditPill ok" : "creditPill warn"}>{qverisConfigured ? t.restReady : t.restPending}</div>
        </div>
      </aside>

      <section className="contentSurface">
        {activeView === "trading" ? (
          <WorkbenchHome
            t={t}
            query={query}
            setQuery={setQuery}
            newsText={newsText}
            setNewsText={setNewsText}
            strategyId={strategyId}
            setStrategyId={setStrategyId}
            startDate={startDate}
            setStartDate={setStartDate}
            endDate={endDate}
            setEndDate={setEndDate}
            initialCash={initialCash}
            setInitialCash={setInitialCash}
            maxDrawdown={maxDrawdown}
            setMaxDrawdown={setMaxDrawdown}
            templates={templates}
            recommendations={recommendationCards}
            result={result}
            chartData={chartData}
            loading={loading}
            runningStepIndex={runningStepIndex}
            confirming={confirming}
            message={message}
            onRun={handleRun}
            onConfirm={handleConfirm}
            onPickRecommendation={applyRecommendation}
            onTrackRecent={trackRecent}
          />
        ) : null}
        {activeView === "research" ? (
          <PageScaffold eyebrow={t.industrySubtitle} title={t.industryTitle}>
            <IndustryResearch
              t={t}
              industry={industry}
              industryTheme={industryTheme}
              setIndustryTheme={setIndustryTheme}
            />
          </PageScaffold>
        ) : null}
        {activeView === "settings" ? (
          <PageScaffold eyebrow={t.heroEyebrow} title={t.systemSettings}>
            <SettingsDesk
              t={t}
              language={language}
              setLanguage={setLanguage}
              systemStatus={systemStatus}
              systemConfig={systemConfig}
              savingConfig={savingConfig}
              configMessage={configMessage}
              onSaveConfig={handleSaveSystemConfig}
            />
          </PageScaffold>
        ) : null}
      </section>
    </main>
  );
}

function WorkbenchHome({
  t,
  query,
  setQuery,
  newsText,
  setNewsText,
  strategyId,
  setStrategyId,
  startDate,
  setStartDate,
  endDate,
  setEndDate,
  initialCash,
  setInitialCash,
  maxDrawdown,
  setMaxDrawdown,
  templates,
  recommendations,
  result,
  chartData,
  loading,
  runningStepIndex,
  confirming,
  message,
  onRun,
  onConfirm,
  onPickRecommendation,
  onTrackRecent
}: {
  t: Record<string, string>;
  query: string;
  setQuery: (query: string) => void;
  newsText: string;
  setNewsText: (newsText: string) => void;
  strategyId: string;
  setStrategyId: (strategyId: string) => void;
  startDate: string;
  setStartDate: (date: string) => void;
  endDate: string;
  setEndDate: (date: string) => void;
  initialCash: number;
  setInitialCash: (cash: number) => void;
  maxDrawdown: number;
  setMaxDrawdown: (drawdown: number) => void;
  templates: StrategyTemplate[];
  recommendations: Array<{ title: string; source: string; summary: string; signal: string; query: string; strategyId: string }>;
  result: AgentRunResponse | null;
  chartData: Array<{ date: string; value: number; drawdown: number }>;
  loading: boolean;
  runningStepIndex: number;
  confirming: boolean;
  message: string;
  onRun: () => void;
  onConfirm: () => void;
  onPickRecommendation: (card: { title: string; query: string; summary: string; strategyId: string }) => void;
  onTrackRecent: (item: RecentItem) => void;
}) {
  const selectedTemplate = templates.find((template) => template.id === strategyId);

  function syncPresetQuery(patch: { startDate?: string; endDate?: string; initialCash?: number; maxDrawdown?: number }) {
    if (!selectedTemplate || !query.startsWith(presetQueryPrefix(selectedTemplate))) return;
    const nextStart = patch.startDate ?? startDate;
    const nextEnd = patch.endDate ?? endDate;
    const nextQuery = buildPresetQuery(
      selectedTemplate,
      nextStart,
      nextEnd,
      patch.initialCash ?? initialCash,
      patch.maxDrawdown ?? maxDrawdown
    );
    setQuery(nextQuery);
    onTrackRecent({
      title: strategyDisplayName(selectedTemplate),
      detail: `${nextStart} - ${nextEnd}`,
      query: nextQuery,
      strategyId: selectedTemplate.id
    });
  }

  function pickTemplate(template: StrategyTemplate) {
    const nextQuery = buildPresetQuery(template, startDate, endDate, initialCash, maxDrawdown);
    setStrategyId(template.id);
    setQuery(nextQuery);
    onTrackRecent({
      title: strategyDisplayName(template),
      detail: `${template.benchmark} / ${t.topN} ${template.top_n}`,
      query: nextQuery,
      strategyId: template.id
    });
  }

  function handleStartDateChange(value: string) {
    setStartDate(value);
    syncPresetQuery({ startDate: value });
  }

  function handleEndDateChange(value: string) {
    setEndDate(value);
    syncPresetQuery({ endDate: value });
  }

  function handleInitialCashChange(value: number) {
    setInitialCash(value);
    syncPresetQuery({ initialCash: value });
  }

  function handleMaxDrawdownChange(value: number) {
    setMaxDrawdown(value);
    syncPresetQuery({ maxDrawdown: value });
  }

  return (
    <>
      <section className="creatorHero">
        <div className="heroShade" />
        <div className="heroInner">
          <h1>{t.createTitle}</h1>
          <div className="composer">
            <div className="composerIcon">
              <Search size={20} />
            </div>
            <textarea value={query} onChange={(event) => setQuery(event.target.value)} rows={2} placeholder={t.promptPlaceholder} />
            <button className="generateButton" onClick={onRun} disabled={loading}>
              {loading ? <RefreshCw className="spin" size={19} /> : <SendHorizontal size={19} />}
              <span>{loading ? t.running : t.generate}</span>
            </button>
          </div>
          {loading ? <RunProgress t={t} activeIndex={runningStepIndex} /> : null}
          {message ? <div className="toastMessage">{message}</div> : null}
        </div>
      </section>

      <section className="presetSection">
        <div className="sectionHead">
          <h2>{t.presetStrategies}</h2>
          <span>{templates.length} {t.templateCount}</span>
        </div>
        <div className="presetGrid">
          {templates.map((template) => (
            <button className={strategyId === template.id ? "presetCard active" : "presetCard"} key={template.id} onClick={() => pickTemplate(template)}>
              <div>
                <strong>{strategyDisplayName(template)}</strong>
                <span>{template.category}</span>
              </div>
              <p>{strategySummary(template)}</p>
              <em>{template.benchmark} / {t.topN} {template.top_n}</em>
            </button>
          ))}
        </div>
      </section>

      {!result && !loading ? (
        <section className="recommendationSection">
          <div className="sectionHead">
            <h2>{t.recommendations}</h2>
            <span>{t.community}</span>
          </div>
          <div className="recommendationRail">
            {recommendations.map((card, index) => (
              <button className="ideaCard" key={`${card.title}-${index}`} onClick={() => onPickRecommendation(card)}>
                <span className="ideaSignal">{card.signal}</span>
                <strong>{card.title}</strong>
                <p>{card.summary}</p>
                <em>{card.source}</em>
              </button>
            ))}
          </div>
        </section>
      ) : null}

      <section className="controlBand">
        <div className="controlTitle">
          <SlidersHorizontal size={18} />
          <span>{t.advanced}</span>
        </div>
        <div className="controlGrid">
          <label>
            {t.start}
            <input type="date" value={startDate} onChange={(event) => handleStartDateChange(event.target.value)} />
          </label>
          <label>
            {t.end}
            <input type="date" value={endDate} onChange={(event) => handleEndDateChange(event.target.value)} />
          </label>
          <label>
            {t.cash}
            <input type="number" min={1000} step={1000} value={initialCash} onChange={(event) => handleInitialCashChange(Number(event.target.value))} />
          </label>
          <label>
            {t.maxDD}
            <input type="number" min={3} max={60} value={maxDrawdown} onChange={(event) => handleMaxDrawdownChange(Number(event.target.value))} />
          </label>
        </div>
        <label className="newsControl">
          {t.newsInput}
          <textarea value={newsText} onChange={(event) => setNewsText(event.target.value)} rows={3} placeholder={t.newsPlaceholder} />
        </label>
      </section>

      <div className="statusRibbon">
        <Metric label={t.totalReturn} value={result ? pct(result.metrics.total_return) : "0.0%"} />
        <Metric label={t.benchmark} value={result ? pct(result.metrics.benchmark_return) : "0.0%"} />
        <Metric label={t.maxDrawdown} value={result ? pct(Math.abs(result.metrics.max_drawdown)) : "0.0%"} />
        <Metric label={t.sharpe} value={result ? result.metrics.sharpe_ratio.toFixed(2) : "0.00"} />
        <Metric label={t.trades} value={result ? String(result.metrics.number_of_trades) : "0"} />
        <Metric label={t.backtestPeriod} value={result ? `${result.strategy_spec.start_date} - ${result.strategy_spec.end_date}` : `${startDate} - ${endDate}`} compact />
        <Metric label={t.data} value={result?.data_source ?? t.notLoaded} compact />
        <Verdict t={t} decision={verdictLabel(result)} />
      </div>

      <TradingDesk
        t={t}
        result={result}
        chartData={chartData}
        confirming={confirming}
        onConfirm={onConfirm}
      />
    </>
  );
}

function RunProgress({ t, activeIndex }: { t: Record<string, string>; activeIndex: number }) {
  const steps = runProgressSteps(t, activeIndex);
  return (
    <section className="runProgress">
      <div className="runProgressTitle">
        <RefreshCw className="spin" size={15} />
        <span>{t.runProgress}</span>
      </div>
      <div className="runProgressTrack">
        {steps.map((step, index) => (
          <div className={`runProgressStep ${step.status}`} key={step.label}>
            <span>{index + 1}</span>
            <strong>{step.label}</strong>
            <p>{step.detail}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function PageScaffold({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) {
  return (
    <div className="pageScaffold">
      <header className="pageHeader">
        <h1>{title}</h1>
        <p className="eyebrow">{eyebrow}</p>
      </header>
      {children}
    </div>
  );
}

function TradingDesk({
  t,
  result,
  chartData,
  confirming,
  onConfirm
}: {
  t: Record<string, string>;
  result: AgentRunResponse | null;
  chartData: Array<{ date: string; value: number; drawdown: number }>;
  confirming: boolean;
  onConfirm: () => void;
}) {
  return (
    <>
      <div className="boardGrid">
        <section className="panel chartPanel">
          <div className="panelTitle">
            <TrendingUp size={18} />
            <span>{t.equity}</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="equity" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#31d5c8" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#31d5c8" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#e7e7e7" strokeDasharray="3 3" />
              <XAxis dataKey="date" stroke="#737373" minTickGap={30} />
              <YAxis stroke="#737373" tickFormatter={(value) => `${Math.round(Number(value) / 1000)}k`} width={52} />
              <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #e0e0e0", borderRadius: 8, color: "#1f1f1f" }} />
              <Area type="monotone" dataKey="value" stroke="#111111" strokeWidth={2} fill="url(#equity)" />
            </AreaChart>
          </ResponsiveContainer>
        </section>

        <section className="panel chartPanel">
          <div className="panelTitle">
            <ShieldAlert size={18} />
            <span>{t.drawdown}</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={chartData}>
              <CartesianGrid stroke="#e7e7e7" strokeDasharray="3 3" />
              <XAxis dataKey="date" stroke="#737373" minTickGap={30} />
              <YAxis stroke="#737373" tickFormatter={(value) => pct(Number(value))} width={58} />
              <Tooltip contentStyle={{ background: "#ffffff", border: "1px solid #e0e0e0", borderRadius: 8, color: "#1f1f1f" }} formatter={(value) => pct(Number(value))} />
              <Line type="monotone" dataKey="drawdown" stroke="#ff6b81" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </section>
      </div>

      <div className="boardGrid lower">
        <section className="panel fullPanel">
          <div className="panelTitle">
            <ShieldCheck size={18} />
            <span>{t.riskVerdict}</span>
          </div>
          {result ? (
            <>
              <p className="explanation">{result.explanation}</p>
              <div className={`riskDecision ${result.risk.decision.toLowerCase()}`}>
                <strong>{decisionLabel(t, result.risk.decision)}</strong>
                <span>{result.risk.reasons[0]}</span>
              </div>
              <div className="riskLogHeader">
                <ShieldCheck size={16} />
                <span>{t.riskLog}</span>
              </div>
              <div className="riskLogTable">
                <div className="riskLogRow head">
                  <span>{t.riskLog}</span>
                  <span>{t.actual}</span>
                  <span>{t.limit}</span>
                  <span>{t.status}</span>
                </div>
                {result.risk.checks.map((check) => (
                  <div className={check.passed ? "riskLogRow pass" : "riskLogRow fail"} key={check.name}>
                    <span>{riskCheckLabel(check.name)}</span>
                    <strong>{riskCheckValue(check.name, check.value)}</strong>
                    <strong>{riskCheckValue(check.name, check.limit)}</strong>
                    <em>{riskStatusLabel(t, check.passed, check.severity)}</em>
                  </div>
                ))}
              </div>
              <ul className="reasonList">
                {result.risk.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
              <p className="suggestedAction"><strong>{t.suggestedAction}</strong>{result.risk.suggested_action}</p>
            </>
          ) : (
            <p className="emptyText">{t.emptyRisk}</p>
          )}
        </section>

      </div>

      <div className="boardGrid lower">
        <section className="panel">
          <div className="panelTitle">
            <BarChart3 size={18} />
            <span>{t.factorRankings}</span>
          </div>
          <div className="tableWrap">
            <table>
              <thead>
                <tr>
                  <th>{t.symbol}</th>
                  <th>{t.score}</th>
                  <th>Mom 60D</th>
                  <th>{t.trend}</th>
                  <th>{t.quality}</th>
                  <th>{t.event}</th>
                </tr>
              </thead>
              <tbody>
                {(result?.factor_rankings ?? []).map((row) => (
                  <tr key={String(row.symbol)}>
                    <td>{row.symbol}</td>
                    <td>{Number(row.score).toFixed(2)}</td>
                    <td>{pct(Number(row.momentum_60d ?? 0))}</td>
                    <td>{pct(Number(row.trend_ma60 ?? 0))}</td>
                    <td>{Number(row.fundamental_quality ?? 0).toFixed(2)}</td>
                    <td>{Number(row.event_score ?? 0).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!result ? <p className="emptyText">{t.noRanking}</p> : null}
          </div>
        </section>

        <section className="panel">
          <div className="panelTitle">
            <WalletCards size={18} />
            <span>{t.portfolioWeights}</span>
          </div>
          <div className="weightList">
            {Object.entries(result?.target_weights ?? {}).map(([symbol, weight]) => (
              <div className="weightRow" key={symbol}>
                <span>{symbol}</span>
                <div className="barTrack">
                  <div style={{ width: `${Math.min(100, weight * 100)}%` }} />
                </div>
                <strong>{pct(weight)}</strong>
              </div>
            ))}
            {result ? (
              <div className="weightRow cash">
                <span>{t.cashLabel}</span>
                <div className="barTrack">
                  <div style={{ width: `${(result.strategy_spec.risk_limits.cash_buffer || 0) * 100}%` }} />
                </div>
                <strong>{pct(result.strategy_spec.risk_limits.cash_buffer)}</strong>
              </div>
            ) : null}
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panelTitle">
          <CheckCircle2 size={18} />
          <span>{t.orderPreview}</span>
        </div>
        <div className="orderList">
          {(result?.orders ?? []).map((order) => (
            <div className="orderRow" key={order.symbol}>
              <div>
                <strong>{order.symbol}</strong>
                <span>{orderSideLabel(t, order.side)} / {pct(order.target_weight)} / stop {pct(order.stop_loss)}</span>
              </div>
              <div>
                <strong>{order.estimated_quantity}</strong>
                <span>{money(order.estimated_notional)}</span>
              </div>
            </div>
          ))}
          {result && result.orders.length === 0 ? <p className="emptyText">{t.rejected}</p> : null}
        </div>
        <button className="confirmButton" onClick={onConfirm} disabled={!result || result.orders.length === 0 || confirming}>
          {confirming ? <RefreshCw className="spin" size={18} /> : <CheckCircle2 size={18} />}
          {t.confirm}
        </button>
      </section>
    </>
  );
}

function IndustryResearch({
  t,
  industry,
  industryTheme,
  setIndustryTheme
}: {
  t: Record<string, string>;
  industry: IndustryChainResponse | null;
  industryTheme: "ai" | "robotics";
  setIndustryTheme: (theme: "ai" | "robotics") => void;
}) {
  return (
    <>
      <div className="researchToolbar">
        <button className={industryTheme === "ai" ? "active" : ""} onClick={() => setIndustryTheme("ai")}>
          <Cpu size={16} />
          {t.aiChain}
        </button>
        <button className={industryTheme === "robotics" ? "active" : ""} onClick={() => setIndustryTheme("robotics")}>
          <Bot size={16} />
          {t.roboticsChain}
        </button>
      </div>

      <div className="metricGrid researchMetrics">
        {(industry?.scarce_layers ?? []).map((layer) => (
          <Metric key={layer} label={t.scarceLayers} value={layer} compact />
        ))}
      </div>

      <div className="boardGrid lower">
        <section className="panel">
          <div className="panelTitle">
            <Layers3 size={18} />
            <span>{t.valueChain}</span>
          </div>
          <div className="layerList">
            {(industry?.layers ?? []).map((layer) => (
              <div className="layerRow" key={layer.id}>
                <div>
                  <strong>{layer.name}</strong>
                  <span>{localizedToken(t, layer.direction)} / score {layer.bottleneck_score.toFixed(2)}</span>
                  <p>{layer.why_it_matters}</p>
                </div>
                <div className="miniTags">
                  {layer.key_metrics.map((metric) => (
                    <span key={metric}>{metric}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panelTitle">
            <ShieldCheck size={18} />
            <span>{t.methodology}</span>
          </div>
          <p className="explanation">{industry?.summary}</p>
          <p className="explanation mutedBlock">{industry?.methodology}</p>
          <p className="emptyText">{industry?.disclaimer}</p>
        </section>
      </div>

      <section className="panel">
        <div className="panelTitle">
          <Database size={18} />
          <span>{t.valuationTable}</span>
        </div>
        <div className="tableWrap">
          <table>
            <thead>
              <tr>
                <th>{t.symbol}</th>
                <th>{t.category}</th>
                <th>{t.marketCap}</th>
                <th>PE</th>
                <th>PS</th>
                <th>PEG</th>
                <th>{t.growth}</th>
                <th>{t.grossMargin}</th>
                <th>{t.priority}</th>
                <th>{t.evidence}</th>
                <th>{t.keyMetric}</th>
                <th>{t.risk}</th>
              </tr>
            </thead>
            <tbody>
              {(industry?.companies ?? []).map((company) => (
                <tr key={`${company.symbol}-${company.layer}`}>
                  <td>
                    <strong>{company.symbol}</strong>
                    <span className="subCell">{company.name}</span>
                  </td>
                  <td>
                    {company.category}
                    <span className={`signal ${company.valuation_signal}`}>{localizedToken(t, company.valuation_signal)}</span>
                  </td>
                  <td>{bn(company.market_cap_usd_bn)}</td>
                  <td>{ratio(company.pe)}</td>
                  <td>{ratio(company.ps)}</td>
                  <td>{ratio(company.peg)}</td>
                  <td>{company.revenue_growth === null ? "-" : pct(company.revenue_growth)}</td>
                  <td>{company.gross_margin === null ? "-" : pct(company.gross_margin)}</td>
                  <td>{company.research_priority.toFixed(2)}</td>
                  <td>{localizedToken(t, company.evidence_strength)}</td>
                  <td>{company.key_metric}</td>
                  <td>{company.risk}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function SettingsDesk({
  t,
  language,
  setLanguage,
  systemStatus,
  systemConfig,
  savingConfig,
  configMessage,
  onSaveConfig
}: {
  t: Record<string, string>;
  language: Language;
  setLanguage: (language: Language) => void;
  systemStatus: SystemStatus | null;
  systemConfig: SystemConfig | null;
  savingConfig: boolean;
  configMessage: string;
  onSaveConfig: (config: SystemConfig) => void;
}) {
  const [draft, setDraft] = useState<SystemConfig | null>(systemConfig);
  const arkConfigured = systemStatus?.volc_ark.configured ?? systemConfig?.volc_ark.configured;
  const qverisConfigured = Boolean(systemStatus?.qveris.configured ?? systemConfig?.qveris.configured);
  const qverisMode = typeof systemStatus?.qveris.mode === "string" ? systemStatus.qveris.mode : "rest";

  useEffect(() => {
    setDraft(systemConfig);
  }, [systemConfig]);

  function updateVolc(patch: Partial<SystemConfig["volc_ark"]>) {
    setDraft((current) => current ? { ...current, volc_ark: { ...current.volc_ark, ...patch } } : current);
  }

  function updateQveris(patch: Partial<SystemConfig["qveris"]>) {
    setDraft((current) => current ? { ...current, qveris: { ...current.qveris, ...patch } } : current);
  }

  function updateDataSource(id: string, patch: Partial<DataSourceConfig>) {
    setDraft((current) => current
      ? {
          ...current,
          data_sources: current.data_sources.map((row) => row.id === id ? { ...row, ...patch } : row)
        }
      : current);
  }

  return (
    <div className="settingsStack">
      <div className="settingsGrid">
        <section className="panel">
          <div className="panelTitle">
            <Languages size={18} />
            <span>{t.language}</span>
          </div>
          <div className="settingsRow">
            <span>中文</span>
            <button className={language === "zh" ? "smallToggle active" : "smallToggle"} onClick={() => setLanguage("zh")}>ON</button>
          </div>
          <div className="settingsRow">
            <span>English</span>
            <button className={language === "en" ? "smallToggle active" : "smallToggle"} onClick={() => setLanguage("en")}>ON</button>
          </div>
        </section>

        <section className="panel">
          <div className="panelTitle">
            <ShieldCheck size={18} />
            <span>{t.sourcePolicy}</span>
          </div>
          <div className="settingsRow"><span>{t.paperOnly}</span><strong>{systemStatus?.paper_trading_only ? t.enforced : t.disabled}</strong></div>
          <div className="settingsRow"><span>Backtest engine</span><strong>{systemStatus?.backtest_engine ?? "vectorbt 0.28.2"}</strong></div>
          <div className="settingsRow"><span>{t.volcProvider}</span><strong className={arkConfigured ? "stateOk" : "stateWarn"}>{systemStatus ? (arkConfigured ? t.configured : t.notConfigured) : t.checking}</strong></div>
          <div className="settingsRow"><span>{t.qveris}</span><strong className={qverisConfigured ? "stateOk" : "stateWarn"}>{systemStatus ? (qverisConfigured ? `${t.configured} / ${qverisMode}` : t.notConfigured) : t.checking}</strong></div>
        </section>
      </div>

      <section className="panel configPanel">
        <div className="panelTitle">
          <Bot size={18} />
          <span>{t.modelProvider}</span>
        </div>
        <div className="configGrid">
          <label>
            {t.volcProvider} {t.apiKey}
            <input
              className="secretInput"
              type="password"
              value={draft?.volc_ark.api_key ?? ""}
              placeholder={draft?.volc_ark.api_key_masked || "ark-..."}
              onChange={(event) => updateVolc({ api_key: event.target.value })}
            />
          </label>
          <label>
            {t.model}
            <select value={draft?.volc_ark.model ?? "doubao-seed-2-1-pro-260628"} onChange={(event) => updateVolc({ model: event.target.value })}>
              <option value="doubao-seed-2-1-pro-260628">doubao-seed-2-1-pro-260628</option>
              <option value="doubao-seed-2-1-turbo-260628">doubao-seed-2-1-turbo-260628</option>
            </select>
          </label>
          <label>
            {t.volcProvider} {t.apiBase}
            <input value={draft?.volc_ark.base_url ?? ""} onChange={(event) => updateVolc({ base_url: event.target.value })} placeholder="https://ark.cn-beijing.volces.com/api/v3" />
          </label>
          <label>
            {t.qveris} {t.apiKey}
            <input
              className="secretInput"
              type="password"
              value={draft?.qveris.api_key ?? ""}
              placeholder={draft?.qveris.api_key_masked || "sk-..."}
              onChange={(event) => updateQveris({ api_key: event.target.value })}
            />
          </label>
          <label>
            {t.qveris} {t.apiBase}
            <input value={draft?.qveris.base_url ?? ""} onChange={(event) => updateQveris({ base_url: event.target.value })} placeholder="https://qveris.ai/api/v1" />
          </label>
        </div>
      </section>

      <section className="panel">
        <div className="panelTitle">
          <Database size={18} />
          <span>{t.dataSourcePortfolio}</span>
        </div>
        <div className="tableWrap configTableWrap">
          <table className="dataSourceTable">
            <thead>
              <tr>
                <th>{t.target}</th>
                <th>{t.recommendedCombo}</th>
                <th>{t.reason}</th>
                <th>{t.riskPoint}</th>
              </tr>
            </thead>
            <tbody>
              {(draft?.data_sources ?? []).map((row) => (
                <tr key={row.id}>
                  <td>
                    <div className="sourceTargetCell">
                      <label className="sourceCheck">
                        <input type="checkbox" checked={row.enabled} onChange={(event) => updateDataSource(row.id, { enabled: event.target.checked })} />
                        <span>{t.enabled}</span>
                      </label>
                      <input value={row.target} onChange={(event) => updateDataSource(row.id, { target: event.target.value })} />
                    </div>
                  </td>
                  <td>
                    <textarea
                      value={row.recommended_combo}
                      rows={2}
                      onChange={(event) => updateDataSource(row.id, { recommended_combo: event.target.value, providers: splitProviders(event.target.value) })}
                    />
                    <label className="providerField">
                      <span>{t.providers}</span>
                      <input value={row.providers.join(", ")} onChange={(event) => updateDataSource(row.id, { providers: splitProviders(event.target.value) })} />
                    </label>
                  </td>
                  <td>
                    <textarea value={row.reason} rows={2} onChange={(event) => updateDataSource(row.id, { reason: event.target.value })} />
                  </td>
                  <td>
                    <textarea value={row.risk} rows={2} onChange={(event) => updateDataSource(row.id, { risk: event.target.value })} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="configActions">
        <button className="confirmButton" onClick={() => draft && onSaveConfig(draft)} disabled={!draft || savingConfig}>
          {savingConfig ? <RefreshCw className="spin" size={18} /> : <CheckCircle2 size={18} />}
          {savingConfig ? t.savingSettings : t.saveSettings}
        </button>
        {configMessage ? <span>{configMessage}</span> : null}
      </div>
    </div>
  );
}

function Metric({ label, value, compact }: { label: string; value: string; compact?: boolean }) {
  return (
    <div className={compact ? "metric compact" : "metric"}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Verdict({ t, decision }: { t: Record<string, string>; decision: "ALLOW" | "WATCH" | "REJECT" }) {
  return <div className={`verdict ${decision.toLowerCase()}`}>{decisionLabel(t, decision)}</div>;
}
