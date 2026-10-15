/**
 * Unified API Client for Enterprise Decision Intelligence Platform
 * Automatically connects to live FastAPI backend when available,
 * and falls back to interactive client-side decision engine on standalone static hosts (e.g. Netlify).
 */
import {
  mockKPIs,
  mockTimeSeries,
  mockMonthlySales,
  mockCategories,
  mockRegions,
  mockCustomerSegments,
  mockHighRiskCustomers,
  mockInventoryHealth,
  mockStockoutSummary,
  mockForecastBenchmarks,
  mockFutureForecast,
  mockAnomalies,
  mockDataQualityLogs,
  mockModelDrift,
  mockChurnExplainability,
  resolveAgentQuery
} from "./mockData";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Global connection state flag
export let isLiveBackendConnected = false;

// Helper to provide realistic response latency in demo mode
const simulateLatency = (ms = 400) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchJson(endpoint, options = {}) {
  // If we already know the backend is not reachable in this session and no custom URL was provided,
  // we can immediately return high-fidelity fallback data without browser network console errors.
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 3500);

  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...options,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP Error ${res.status}`);
    }
    const payload = await res.json();
    isLiveBackendConnected = true;
    return payload.data !== undefined ? payload.data : payload;
  } catch (error) {
    clearTimeout(timeoutId);
    isLiveBackendConnected = false;
    console.info(`[Decision AI Engine] Backend at ${API_BASE_URL} unreachable (${error.message}). Serving interactive cloud demo data for ${endpoint}.`);
    
    // Provide a brief realistic delay for interactive feel
    await simulateLatency(endpoint.includes("inquire") ? 800 : 250);
    return getFallbackData(endpoint, options);
  }
}

function getFallbackData(endpoint, options = {}) {
  // AI Agent endpoints
  if (endpoint.includes("/api/agent/inquire")) {
    let question = "";
    if (options.body) {
      try {
        const parsed = JSON.parse(options.body);
        question = parsed.question || "";
      } catch (e) {
        question = "";
      }
    }
    return resolveAgentQuery(question);
  }

  if (endpoint.includes("/api/agent/sql")) {
    return {
      success: true,
      sql: "SELECT category, SUM(profit) FROM fact_sales GROUP BY category;",
      row_count: 5,
      chart_ready: {
        chart_type: "bar",
        x_key: "category",
        y_key: "profit",
        series: mockCategories
      }
    };
  }

  if (endpoint.includes("/api/agent/rag")) {
    return resolveAgentQuery("return policy");
  }

  // Dashboard KPI & Time-Series endpoints
  if (endpoint.includes("/api/kpi/summary")) return mockKPIs;
  if (endpoint.includes("/api/kpi/time-series")) return mockTimeSeries;

  // Sales endpoints
  if (endpoint.includes("/api/sales/monthly-trend")) return { monthly_trend: mockMonthlySales };
  if (endpoint.includes("/api/sales/category-performance")) return mockCategories;
  if (endpoint.includes("/api/sales/regional-performance")) return mockRegions;

  // Customer endpoints
  if (endpoint.includes("/api/customers/segments")) return mockCustomerSegments;
  if (endpoint.includes("/api/customers/high-value-high-risk")) return mockHighRiskCustomers;
  if (endpoint.includes("/api/customers/churn-risk-distribution")) return mockCustomerSegments;

  // Inventory endpoints
  if (endpoint.includes("/api/inventory/health")) return mockInventoryHealth;
  if (endpoint.includes("/api/inventory/stockout-summary")) return mockStockoutSummary;

  // Forecasting endpoints
  if (endpoint.includes("/api/forecast/future")) return mockFutureForecast;
  if (endpoint.includes("/api/forecast/benchmarks")) return mockForecastBenchmarks;

  // Alerts & Quality endpoints
  if (endpoint.includes("/api/alerts/anomalies")) return mockAnomalies;
  if (endpoint.includes("/api/alerts/data-quality")) return mockDataQualityLogs;

  // Models & Monitoring
  if (endpoint.includes("/api/models/monitoring/drift")) return mockModelDrift;
  if (endpoint.includes("/api/models/explainability/churn")) return mockChurnExplainability;

  return null;
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
