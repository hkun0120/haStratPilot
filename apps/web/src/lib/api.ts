import type { AgentRunResponse, IndustryChainResponse, OrderPreview, RiskVerdict, StrategySpec, StrategyTemplate, SystemConfig, SystemStatus } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? (process.env.NODE_ENV === "production" ? "" : "http://localhost:8000");

export async function fetchTemplates(): Promise<StrategyTemplate[]> {
  const response = await fetch(`${API_BASE}/api/strategy/templates`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch templates");
  const data = await response.json();
  return data.templates;
}

export async function fetchHotNews() {
  const response = await fetch(`${API_BASE}/api/news/hotspots`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch news");
  return (await response.json()).items;
}

export async function fetchIndustryChain(theme: "ai" | "robotics", language: "zh" | "en" = "zh"): Promise<IndustryChainResponse> {
  const response = await fetch(`${API_BASE}/api/research/industry-chain?theme=${theme}&language=${language}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch industry chain");
  return response.json();
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const response = await fetch(`${API_BASE}/api/system/status`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch system status");
  return response.json();
}

export async function fetchSystemConfig(): Promise<SystemConfig> {
  const response = await fetch(`${API_BASE}/api/system/config`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch system config");
  return response.json();
}

export async function saveSystemConfig(payload: SystemConfig): Promise<SystemConfig> {
  const response = await fetch(`${API_BASE}/api/system/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error("Failed to save system config");
  return response.json();
}

export async function runAgent(payload: {
  query: string;
  news_text?: string;
  strategy_id?: string;
  start_date?: string;
  end_date?: string;
  initial_cash: number;
  max_drawdown?: number;
}): Promise<AgentRunResponse> {
  const response = await fetch(`${API_BASE}/api/agent/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const text = await response.text();
    let detail = text;
    try {
      const data = JSON.parse(text);
      detail = data.detail || text;
    } catch {
      detail = text;
    }
    throw new Error(detail || "Agent run failed");
  }
  return response.json();
}

export async function confirmOrders(payload: {
  run_id: string;
  orders: OrderPreview[];
  strategy_spec: StrategySpec;
  metrics: AgentRunResponse["metrics"];
  risk: RiskVerdict;
}) {
  const response = await fetch(`${API_BASE}/api/orders/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error("Failed to confirm orders");
  return response.json();
}
