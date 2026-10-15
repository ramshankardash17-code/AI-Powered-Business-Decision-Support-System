/**
 * Unified API Client for Enterprise Decision Intelligence Platform
 */
const API_BASE_URL = "http://localhost:8000";

async function fetchJson(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP Error ${res.status}`);
    }
    const payload = await res.json();
    return payload.data !== undefined ? payload.data : payload;
  } catch (error) {
    console.warn(`API call to ${endpoint} failed:`, error.message);
    throw error;
  }
}

export const api = {
  // KPIs
  getExecutiveKPIs: () => fetchJson("/api/kpi/summary"),
  getTimeSeriesMetrics: () => fetchJson("/api/kpi/time-series"),

  // Sales
  getMonthlySales: () => fetchJson("/api/sales/monthly-trend"),
  getCategoryPerformance: () => fetchJson("/api/sales/category-performance"),
  getRegionalPerformance: () => fetchJson("/api/sales/regional-performance"),

  // Customers
  getCustomerSegments: () => fetchJson("/api/customers/segments"),
  getHighValueHighRisk: () => fetchJson("/api/customers/high-value-high-risk"),
  getChurnDistribution: () => fetchJson("/api/customers/churn-risk-distribution"),

  // Inventory
  getInventoryHealth: () => fetchJson("/api/inventory/health"),
  getStockoutSummary: () => fetchJson("/api/inventory/stockout-summary"),

  // Marketing
  getMarketingROI: () => fetchJson("/api/marketing/roi"),

  // Forecasting
  getFutureForecast: (days = 30) => fetchJson(`/api/forecast/future?horizon_days=${days}`),
  getForecastBenchmarks: () => fetchJson("/api/forecast/benchmarks"),

  // Alerts & Quality
  getAnomalies: () => fetchJson("/api/alerts/anomalies"),
  getDataQualityLogs: () => fetchJson("/api/alerts/data-quality"),

  // Models & Monitoring
  getModelDrift: () => fetchJson("/api/models/monitoring/drift"),
  getChurnExplainability: () => fetchJson("/api/models/explainability/churn"),

  // AI Business Analyst
  askAgent: (question) =>
    fetchJson("/api/agent/inquire", {
      method: "POST",
      body: JSON.stringify({ question }),
    }),

  executeSafeSQL: (query) =>
    fetchJson("/api/agent/sql", {
      method: "POST",
      body: JSON.stringify({ query }),
    }),

  queryPolicyRAG: (question) =>
    fetchJson("/api/agent/rag", {
      method: "POST",
      body: JSON.stringify({ question, top_k: 3 }),
    }),
};
