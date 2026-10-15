import React, { useState, useEffect } from "react";
import {
  LayoutDashboard,
  TrendingUp,
  Users,
  Package,
  Megaphone,
  Boxes,
  LineChart as LineChartIcon,
  Bot,
  AlertTriangle,
  FileText,
  Cpu,
  ChevronRight,
  Sparkles,
  Search,
  Database,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  CheckCircle2,
  ExternalLink,
  ShieldCheck,
  Send,
  Code
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell
} from "recharts";
import { api, isLiveBackendConnected } from "./api/client";

const COLORS = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e", "#a855f7"];

export default function App() {
  const [activeTab, setActiveTab] = useState("analyst"); // Default to flagship AI Analyst
  const [loading, setLoading] = useState(false);
  const [backendLive, setBackendLive] = useState(false);
  const [execKPIs, setExecKPIs] = useState(null);
  const [salesTrend, setSalesTrend] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [customerSegments, setCustomerSegments] = useState([]);
  const [highRiskCustomers, setHighRiskCustomers] = useState(null);
  const [inventoryHealth, setInventoryHealth] = useState([]);
  const [stockoutSummary, setStockoutSummary] = useState(null);
  const [futureForecast, setFutureForecast] = useState([]);
  const [forecastBenchmarks, setForecastBenchmarks] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [dataQualityLogs, setDataQualityLogs] = useState([]);
  const [modelDrift, setModelDrift] = useState(null);
  const [churnFeatureImportance, setChurnFeatureImportance] = useState([]);

  // AI Analyst Chat State
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    {
      sender: "ai",
      type: "intro",
      content:
        "Welcome to the **Enterprise AI Business Decision Intelligence Platform**. I am your AI Business Analyst. I can answer complex root-cause inquiries, execute safe SQL queries, evaluate ML churn models, run LSTM demand forecasts, and look up company SOPs.",
      suggestions: [
        "Why did profit decrease last month?",
        "Which customers are at risk and what should we do?",
        "What will sales look like next month?",
        "What does our return policy say about electronics?",
        "Show the top 10 products by profit in South"
      ]
    }
  ]);
  const [activeSqlModal, setActiveSqlModal] = useState(null);

  // Initial Data Fetch
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [kpiRes, trendRes, catRes, segRes, highRiskRes, invRes, invSumRes, fcRes, bmRes, anomRes, dqRes, driftRes, fiRes] =
        await Promise.allSettled([
          api.getExecutiveKPIs(),
          api.getMonthlySales(),
          api.getCategoryPerformance(),
          api.getCustomerSegments(),
          api.getHighValueHighRisk(),
          api.getInventoryHealth(),
          api.getStockoutSummary(),
          api.getFutureForecast(30),
          api.getForecastBenchmarks(),
          api.getAnomalies(),
          api.getDataQualityLogs(),
          api.getModelDrift(),
          api.getChurnExplainability()
        ]);

      if (kpiRes.status === "fulfilled") setExecKPIs(kpiRes.value);
      if (trendRes.status === "fulfilled") setSalesTrend(trendRes.value?.monthly_trend || []);
      if (catRes.status === "fulfilled") setCategoryData(catRes.value || []);
      if (segRes.status === "fulfilled") setCustomerSegments(segRes.value || []);
      if (highRiskRes.status === "fulfilled") setHighRiskCustomers(highRiskRes.value);
      if (invRes.status === "fulfilled") setInventoryHealth(invRes.value || []);
      if (invSumRes.status === "fulfilled") setStockoutSummary(invSumRes.value);
      if (fcRes.status === "fulfilled") setFutureForecast(fcRes.value || []);
      if (bmRes.status === "fulfilled") setForecastBenchmarks(bmRes.value);
      if (anomRes.status === "fulfilled") setAnomalies(anomRes.value || []);
      if (dqRes.status === "fulfilled") setDataQualityLogs(dqRes.value || []);
      if (driftRes.status === "fulfilled") setModelDrift(driftRes.value);
      if (fiRes.status === "fulfilled") setChurnFeatureImportance(fiRes.value?.feature_importance || []);
      setBackendLive(isLiveBackendConnected);
    } catch (e) {
      console.error("Dashboard data load error:", e);
    } finally {
      setLoading(false);
      setBackendLive(isLiveBackendConnected);
    }
  };

  const handleSendChat = async (textToSend) => {
    const query = textToSend || chatInput;
    if (!query.trim()) return;

    const userMsg = { sender: "user", content: query };
    setChatHistory((prev) => [...prev, userMsg]);
    setChatInput("");
    setChatLoading(true);

    try {
      const agentRes = await api.askAgent(query);
      const aiMsg = {
        sender: "ai",
        type: "structured_answer",
        payload: agentRes
      };
      setChatHistory((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = {
        sender: "ai",
        type: "error",
        content: `Error executing analysis: ${err.message}`
      };
      setChatHistory((prev) => [...prev, errorMsg]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand-header">
          <div className="brand-icon-wrapper">
            <Sparkles size={20} color="#fff" />
          </div>
          <div>
            <div className="brand-title">Decision AI</div>
            <div className="brand-badge">Enterprise BI Platform</div>
          </div>
        </div>

        <nav className="nav-menu">
          <div
            className={`nav-item ai-analyst-btn ${activeTab === "analyst" ? "active" : ""}`}
            onClick={() => setActiveTab("analyst")}
          >
            <Bot size={18} />
            <span>AI Business Analyst</span>
          </div>

          <div
            className={`nav-item ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            <LayoutDashboard size={18} />
            <span>Executive Dashboard</span>
          </div>

          <div
            className={`nav-item ${activeTab === "sales" ? "active" : ""}`}
            onClick={() => setActiveTab("sales")}
          >
            <TrendingUp size={18} />
            <span>Sales & Revenue</span>
          </div>

          <div
            className={`nav-item ${activeTab === "customers" ? "active" : ""}`}
            onClick={() => setActiveTab("customers")}
          >
            <Users size={18} />
            <span>Customer Intelligence</span>
          </div>

          <div
            className={`nav-item ${activeTab === "products" ? "active" : ""}`}
            onClick={() => setActiveTab("products")}
          >
            <Package size={18} />
            <span>Products & Returns</span>
          </div>

          <div
            className={`nav-item ${activeTab === "inventory" ? "active" : ""}`}
            onClick={() => setActiveTab("inventory")}
          >
            <Boxes size={18} />
            <span>Inventory Intelligence</span>
          </div>

          <div
            className={`nav-item ${activeTab === "forecasting" ? "active" : ""}`}
            onClick={() => setActiveTab("forecasting")}
          >
            <LineChartIcon size={18} />
            <span>Demand Forecasting</span>
          </div>

          <div
            className={`nav-item ${activeTab === "alerts" ? "active" : ""}`}
            onClick={() => setActiveTab("alerts")}
          >
            <AlertTriangle size={18} />
            <span>Anomalies & Quality</span>
          </div>

          <div
            className={`nav-item ${activeTab === "models" ? "active" : ""}`}
            onClick={() => setActiveTab("models")}
          >
            <Cpu size={18} />
            <span>Model Monitoring</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="system-status-pill">
            <span className="status-dot" style={{ backgroundColor: backendLive ? "#10b981" : "#06b6d4", boxShadow: backendLive ? "0 0 8px #10b981" : "0 0 8px #06b6d4" }}></span>
            <span>{backendLive ? "FastAPI Backend: Online" : "Cloud Demo Engine: Active"}</span>
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
            {backendLive ? "PostgreSQL & Star Schema Connected" : "Interactive Decision AI Engine"}
          </div>
        </div>
      </aside>

      {/* Main Content View */}
      <main className="main-content">
        <header className="top-navbar">
          <div className="page-title-box">
            <h1>
              {activeTab === "analyst" && "AI Business Analyst Assistant"}
              {activeTab === "overview" && "Executive Decision Dashboard"}
              {activeTab === "sales" && "Sales & Revenue Performance"}
              {activeTab === "customers" && "Customer Intelligence & Retention"}
              {activeTab === "products" && "Product Margins & Return Propensity"}
              {activeTab === "inventory" && "Inventory Health & Supply Chain"}
              {activeTab === "forecasting" && "Deep Learning Demand Forecasting"}
              {activeTab === "alerts" && "Enterprise Alerts & Data Quality"}
              {activeTab === "models" && "ML Model Registry & Drift Monitoring"}
            </h1>
            <p>Unified Analytical Intelligence & Machine Learning Architecture</p>
          </div>

          <div className="header-actions">
            <button className="btn btn-secondary" onClick={loadDashboardData} title="Refresh Live Data">
              <RefreshCw size={14} className={loading ? "spin" : ""} />
              <span>Refresh</span>
            </button>
            <div className={`badge ${backendLive ? "badge-info" : "badge-warning"}`}>
              {backendLive ? "Live API Connected" : "Interactive Demo Mode"}
            </div>
          </div>
        </header>

        <div className="page-body">
          {/* ========================================================================= */}
          {/* TAB 1: AI BUSINESS ANALYST (FLAGSHIP CONVERSATIONAL EXPERIENCE)           */}
          {/* ========================================================================= */}
          {activeTab === "analyst" && (
            <div className="analyst-chat-layout">
              <div className="chat-conversation-container">
                <div className="chat-messages">
                  {chatHistory.map((msg, i) => (
                    <div key={i} className={`message-bubble ${msg.sender}`}>
                      <div className={`avatar-box ${msg.sender === "ai" ? "avatar-ai" : "avatar-user"}`}>
                        {msg.sender === "ai" ? <Bot size={20} /> : <Users size={18} />}
                      </div>

                      <div className="message-body">
                        {msg.type === "intro" && (
                          <div>
                            <div style={{ marginBottom: "12px", lineHeight: "1.6" }}>{msg.content}</div>
                            <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "8px" }}>
                              Suggested Inquiries to test multi-agent reasoning:
                            </div>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                              {msg.suggestions.map((sug, sIdx) => (
                                <button
                                  key={sIdx}
                                  className="btn btn-secondary"
                                  style={{ fontSize: "0.78rem", padding: "6px 12px" }}
                                  onClick={() => handleSendChat(sug)}
                                >
                                  <Sparkles size={12} color="var(--accent-cyan)" />
                                  <span>{sug}</span>
                                </button>
                              ))}
                            </div>
                          </div>
                        )}

                        {msg.type === "structured_answer" && (
                          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                            {/* Executive Summary */}
                            <div>
                              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                                <Sparkles size={16} color="var(--accent-cyan)" />
                                <strong style={{ color: "var(--accent-cyan)", fontSize: "0.95rem" }}>Executive Summary</strong>
                              </div>
                              <p style={{ lineHeight: "1.6", color: "var(--text-primary)" }}>
                                {msg.payload.executive_summary}
                              </p>
                            </div>

                            {/* Evidence Cards */}
                            {msg.payload.evidence && msg.payload.evidence.length > 0 && (
                              <div>
                                <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "6px", fontWeight: 600 }}>
                                  Observed Evidence & Statistical Facts
                                </div>
                                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "8px" }}>
                                  {msg.payload.evidence.map((ev, eIdx) => (
                                    <div key={eIdx} className="finding-card" style={{ fontSize: "0.82rem" }}>
                                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                                        <CheckCircle2 size={14} color="var(--accent-emerald)" />
                                        <span>{ev}</span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Root Cause Analysis findings */}
                            {msg.payload.root_cause_analysis && msg.payload.root_cause_analysis.length > 0 && (
                              <div>
                                <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "var(--accent-rose)", marginBottom: "6px", fontWeight: 600 }}>
                                  Root Cause Breakdown Across Dimensions
                                </div>
                                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                                  {msg.payload.root_cause_analysis.map((item, rIdx) => (
                                    <div key={rIdx} className="finding-card">
                                      <div className="finding-header">
                                        <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>{item.dimension}</span>
                                        <span className={`badge ${item.severity === "CRITICAL" ? "badge-critical" : "badge-warning"}`}>
                                          {item.type} ({item.severity})
                                        </span>
                                      </div>
                                      <div style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>{item.finding}</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Chart Payload if available */}
                            {msg.payload.chart_data && (
                              <div style={{ marginTop: "8px" }}>
                                <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "8px", fontWeight: 600 }}>
                                  Visual Evidence ({msg.payload.chart_data.chart_type.toUpperCase()} Chart)
                                </div>
                                <div style={{ height: "240px", width: "100%", backgroundColor: "rgba(0,0,0,0.2)", borderRadius: "var(--radius-sm)", padding: "10px" }}>
                                  <ResponsiveContainer width="100%" height="100%">
                                    {msg.payload.chart_data.chart_type === "line" ? (
                                      <LineChart data={msg.payload.chart_data.series}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                        <XAxis dataKey={msg.payload.chart_data.x_key} stroke="#9ca3af" fontSize={11} />
                                        <YAxis stroke="#9ca3af" fontSize={11} />
                                        <Tooltip contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151" }} />
                                        <Line type="monotone" dataKey={msg.payload.chart_data.y_key} stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} />
                                      </LineChart>
                                    ) : (
                                      <BarChart data={msg.payload.chart_data.series}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                        <XAxis dataKey={msg.payload.chart_data.x_key} stroke="#9ca3af" fontSize={11} />
                                        <YAxis stroke="#9ca3af" fontSize={11} />
                                        <Tooltip contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151" }} />
                                        <Bar dataKey={msg.payload.chart_data.y_key} fill="#6366f1" radius={[4, 4, 0, 0]} />
                                      </BarChart>
                                    )}
                                  </ResponsiveContainer>
                                </div>
                              </div>
                            )}

                            {/* Recommendations */}
                            {msg.payload.recommendations && msg.payload.recommendations.length > 0 && (
                              <div>
                                <div style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "var(--accent-emerald)", marginBottom: "6px", fontWeight: 600 }}>
                                  Actionable Business Recommendations
                                </div>
                                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                                  {msg.payload.recommendations.map((rec, recIdx) => (
                                    <div key={recIdx} className="recommendation-action-card">
                                      <div>
                                        <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{rec.action}</div>
                                        <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{rec.detail}</div>
                                      </div>
                                      <button
                                        className={`btn ${rec.requires_approval ? "btn-primary" : "btn-secondary"}`}
                                        style={{ fontSize: "0.75rem", whiteSpace: "nowrap" }}
                                        onClick={() => alert(`Action '${rec.action}' approved for execution.`)}
                                      >
                                        {rec.requires_approval ? "Approve Action" : "Execute SOP"}
                                      </button>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Sources & SQL Used Toggle */}
                            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingTop: "8px", borderTop: "1px solid var(--border-subtle)" }}>
                              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", fontSize: "0.72rem", color: "var(--text-muted)" }}>
                                <span>Sources:</span>
                                {msg.payload.sources?.map((src, sIdx) => (
                                  <span key={sIdx} className="badge badge-info">{src}</span>
                                ))}
                              </div>

                              {msg.payload.sql_used && (
                                <button
                                  className="btn btn-secondary"
                                  style={{ fontSize: "0.75rem", padding: "4px 8px" }}
                                  onClick={() => setActiveSqlModal(msg.payload.sql_used)}
                                >
                                  <Code size={13} />
                                  <span>View SQL</span>
                                </button>
                              )}
                            </div>

                            {/* Suggested Follow-Ups */}
                            {msg.payload.suggested_follow_up && (
                              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px", marginTop: "4px" }}>
                                {msg.payload.suggested_follow_up.map((sug, sIdx) => (
                                  <button
                                    key={sIdx}
                                    className="btn btn-secondary"
                                    style={{ fontSize: "0.74rem", padding: "4px 10px" }}
                                    onClick={() => handleSendChat(sug)}
                                  >
                                    <ChevronRight size={12} color="var(--accent-indigo)" />
                                    <span>{sug}</span>
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        )}

                        {msg.type === "error" && (
                          <div style={{ color: "var(--accent-rose)", display: "flex", alignItems: "center", gap: "8px" }}>
                            <AlertTriangle size={16} />
                            <span>{msg.content}</span>
                          </div>
                        )}

                        {msg.sender === "user" && <div>{msg.content}</div>}
                      </div>
                    </div>
                  ))}

                  {chatLoading && (
                    <div className="message-bubble ai">
                      <div className="avatar-box avatar-ai">
                        <Bot size={20} />
                      </div>
                      <div className="message-body">
                        <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--text-secondary)" }}>
                          <RefreshCw size={16} className="spin" />
                          <span>Planner Agent decomposing question across SQL, ML, Forecast, and RAG knowledge bases...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="chat-input-bar">
                  <input
                    type="text"
                    className="chat-input"
                    placeholder="Ask any business, forecast, SQL, or churn question (e.g. 'Why did profit decline last month?')..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
                  />
                  <button className="btn btn-primary" onClick={() => handleSendChat()} disabled={chatLoading}>
                    <Send size={16} />
                    <span>Inquire</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* TAB 2: EXECUTIVE DASHBOARD                                                */}
          {/* ========================================================================= */}
          {activeTab === "overview" && (
            <>
              {/* Operational Anomaly Banner if active alerts exist */}
              {anomalies.length > 0 && (
                <div style={{ background: "rgba(244, 63, 94, 0.1)", border: "1px solid rgba(244, 63, 94, 0.3)", borderRadius: "var(--radius-md)", padding: "14px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <AlertTriangle color="var(--accent-rose)" size={20} />
                    <div>
                      <div style={{ fontWeight: 600, color: "var(--accent-rose)" }}>Active Anomaly Alert: {anomalies[0].metric_name}</div>
                      <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{anomalies[0].description}</div>
                    </div>
                  </div>
                  <button className="btn btn-secondary" onClick={() => setActiveTab("alerts")} style={{ fontSize: "0.78rem" }}>
                    Investigate
                  </button>
                </div>
              )}

              {/* 6 Top KPIs */}
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Net Revenue</span>
                    <div className="kpi-icon-box"><TrendingUp size={16} /></div>
                  </div>
                  <div className="kpi-value">${(execKPIs?.net_revenue || 0).toLocaleString()}</div>
                  <div className="kpi-trend trend-up">
                    <ArrowUpRight size={14} />
                    <span>+12.4% vs Previous Year</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Gross Profit</span>
                    <div className="kpi-icon-box"><Sparkles size={16} /></div>
                  </div>
                  <div className="kpi-value">${(execKPIs?.total_profit || 0).toLocaleString()}</div>
                  <div className="kpi-trend trend-down">
                    <ArrowDownRight size={14} />
                    <span>-8.4% Recent Contraction</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Profit Margin</span>
                    <div className="kpi-icon-box"><LineChartIcon size={16} /></div>
                  </div>
                  <div className="kpi-value">{execKPIs?.profit_margin_pct || 0}%</div>
                  <div className="kpi-trend" style={{ color: "var(--text-secondary)" }}>
                    Target Benchmark: 22.0%
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Total Orders</span>
                    <div className="kpi-icon-box"><Package size={16} /></div>
                  </div>
                  <div className="kpi-value">{(execKPIs?.total_orders || 0).toLocaleString()}</div>
                  <div className="kpi-trend trend-up">
                    <span>AOV: ${execKPIs?.avg_order_value || 0}</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Return Rate</span>
                    <div className="kpi-icon-box"><AlertTriangle size={16} /></div>
                  </div>
                  <div className="kpi-value">{execKPIs?.return_rate_pct || 0}%</div>
                  <div className="kpi-trend trend-down">
                    <span>{execKPIs?.total_returns || 0} returned orders</span>
                  </div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Stockout Risk</span>
                    <div className="kpi-icon-box"><Boxes size={16} /></div>
                  </div>
                  <div className="kpi-value">{execKPIs?.stockout_rate_pct || 0}%</div>
                  <div className="kpi-trend trend-down">
                    <span>{execKPIs?.stockout_risk_items || 0} SKUs below safety stock</span>
                  </div>
                </div>
              </div>

              {/* Monthly Trend & Category Split */}
              <div className="charts-grid">
                <div className="chart-card">
                  <div className="chart-card-header">
                    <div>
                      <div className="chart-title">Revenue & Profit Trajectory</div>
                      <div className="chart-subtitle">Historical multi-year performance with festival peaks</div>
                    </div>
                  </div>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={salesTrend}>
                        <defs>
                          <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                          </linearGradient>
                          <linearGradient id="colorProf" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="month_name" stroke="#9ca3af" fontSize={11} />
                        <YAxis stroke="#9ca3af" fontSize={11} />
                        <Tooltip contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151" }} />
                        <Legend />
                        <Area type="monotone" dataKey="revenue" name="Net Revenue ($)" stroke="#6366f1" fillOpacity={1} fill="url(#colorRev)" />
                        <Area type="monotone" dataKey="profit" name="Gross Profit ($)" stroke="#10b981" fillOpacity={1} fill="url(#colorProf)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="chart-card">
                  <div className="chart-card-header">
                    <div>
                      <div className="chart-title">Category Revenue Contribution</div>
                      <div className="chart-subtitle">Share of sales across core merchandising categories</div>
                    </div>
                  </div>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={categoryData}
                          dataKey="revenue"
                          nameKey="category"
                          cx="50%"
                          cy="50%"
                          outerRadius={95}
                          innerRadius={50}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        >
                          {categoryData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151" }} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* ========================================================================= */}
          {/* TAB 3: SALES & REVENUE                                                    */}
          {/* ========================================================================= */}
          {activeTab === "sales" && (
            <div className="page-body" style={{ padding: 0 }}>
              <div className="table-card">
                <div className="chart-card-header">
                  <div>
                    <div className="chart-title">Merchandise Category Margin & Returns Breakdown</div>
                    <div className="chart-subtitle">Direct performance metrics from fact_sales and fact_returns</div>
                  </div>
                </div>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Category</th>
                        <th>Net Revenue</th>
                        <th>Gross Profit</th>
                        <th>Margin %</th>
                        <th>Units Sold</th>
                        <th>Orders Count</th>
                        <th>Return Rate %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {categoryData.map((row, idx) => (
                        <tr key={idx}>
                          <td style={{ fontWeight: 600 }}>{row.category}</td>
                          <td>${Number(row.revenue).toLocaleString()}</td>
                          <td>${Number(row.profit).toLocaleString()}</td>
                          <td>
                            <span className={`badge ${row.profit_margin_pct >= 25 ? "badge-success" : "badge-warning"}`}>
                              {row.profit_margin_pct}%
                            </span>
                          </td>
                          <td>{row.units_sold?.toLocaleString()}</td>
                          <td>{row.orders_count?.toLocaleString()}</td>
                          <td>
                            <span className={`badge ${row.return_rate_pct > 15 ? "badge-critical" : "badge-info"}`}>
                              {row.return_rate_pct}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* TAB 4: CUSTOMER INTELLIGENCE                                              */}
          {/* ========================================================================= */}
          {activeTab === "customers" && (
            <div className="page-body" style={{ padding: 0 }}>
              {/* High Value High Risk Alert Callout */}
              {highRiskCustomers && (
                <div style={{ background: "rgba(244, 63, 94, 0.12)", border: "1px solid rgba(244, 63, 94, 0.3)", borderRadius: "var(--radius-md)", padding: "18px 22px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <h3 style={{ color: "var(--accent-rose)", fontSize: "1.1rem" }}>
                        Critical Retention Matrix: {highRiskCustomers.total_high_value_high_churn_customers} High-Value Customers at Churn Risk
                      </h3>
                      <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "4px" }}>
                        Estimated Lifetime Value at immediate stake: <strong style={{ color: "#fff" }}>${Number(highRiskCustomers.high_risk_clv_at_stake).toLocaleString()}</strong>
                      </p>
                    </div>
                    <button className="btn btn-primary" onClick={() => alert("Retention outreach campaign initiated for VIP accounts.")}>
                      Deploy Retention Campaign
                    </button>
                  </div>
                </div>
              )}

              {/* Customer Segments Table */}
              <div className="table-card">
                <div className="chart-card-header">
                  <div>
                    <div className="chart-title">Customer RFM K-Means Segmentation Profiles</div>
                    <div className="chart-subtitle">Calculated by CustomerSegmentationEngine with Recency, Frequency & Monetary values</div>
                  </div>
                </div>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>RFM Segment</th>
                        <th>Customer Count</th>
                        <th>Avg Spend</th>
                        <th>Avg Orders</th>
                        <th>Avg Recency (Days)</th>
                        <th>Avg Churn Risk %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {customerSegments.map((seg, idx) => (
                        <tr key={idx}>
                          <td style={{ fontWeight: 600 }}>{seg.rfm_segment}</td>
                          <td>{seg.customer_count?.toLocaleString()}</td>
                          <td>${Number(seg.avg_spend).toLocaleString()}</td>
                          <td>{seg.avg_orders}</td>
                          <td>{seg.avg_recency} days</td>
                          <td>
                            <span className={`badge ${seg.avg_churn_pct >= 60 ? "badge-critical" : (seg.avg_churn_pct >= 30 ? "badge-warning" : "badge-success")}`}>
                              {seg.avg_churn_pct}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* TAB 5: INVENTORY INTELLIGENCE                                             */}
          {/* ========================================================================= */}
          {activeTab === "inventory" && (
            <div className="page-body" style={{ padding: 0 }}>
              {stockoutSummary && (
                <div className="kpi-grid">
                  <div className="kpi-card">
                    <div className="kpi-title">Critical Stockouts</div>
                    <div className="kpi-value" style={{ color: "var(--accent-rose)" }}>
                      {stockoutSummary.critical_stockout_skus} SKUs
                    </div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-title">Total Shortage Units</div>
                    <div className="kpi-value">
                      {stockoutSummary.total_shortage_units?.toLocaleString()}
                    </div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-title">Replenishment Capital Required</div>
                    <div className="kpi-value" style={{ color: "var(--accent-amber)" }}>
                      ${Number(stockoutSummary.total_reorder_capital_required).toLocaleString()}
                    </div>
                  </div>
                </div>
              )}

              <div className="table-card">
                <div className="chart-card-header">
                  <div>
                    <div className="chart-title">SKU Replenishment & Stockout Diagnostics</div>
                    <div className="chart-subtitle">30-Day Demand Forecast vs Current Warehouse Inventory</div>
                  </div>
                </div>
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Product SKU</th>
                        <th>Category</th>
                        <th>Current Stock</th>
                        <th>Safety Stock</th>
                        <th>Est. 30D Demand</th>
                        <th>Shortage</th>
                        <th>Recommended Reorder</th>
                        <th>Risk Tier</th>
                      </tr>
                    </thead>
                    <tbody>
                      {inventoryHealth.slice(0, 15).map((row, idx) => (
                        <tr key={idx}>
                          <td style={{ fontWeight: 600 }}>{row.product_name}</td>
                          <td>{row.category}</td>
                          <td>{row.total_current_stock}</td>
                          <td>{row.total_safety_stock}</td>
                          <td>{row.estimated_30d_demand}</td>
                          <td>{row.potential_shortage}</td>
                          <td style={{ fontWeight: 700, color: "var(--accent-cyan)" }}>{row.recommended_reorder_qty} units</td>
                          <td>
                            <span className={`badge ${row.stockout_risk === "CRITICAL" ? "badge-critical" : (row.stockout_risk === "HIGH" ? "badge-warning" : "badge-success")}`}>
                              {row.stockout_risk}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* TAB 6: DEMAND FORECASTING (DEEP LEARNING VS BASELINES)                    */}
          {/* ========================================================================= */}
          {activeTab === "forecasting" && (
            <div className="page-body" style={{ padding: 0 }}>
              <div className="chart-card full-width">
                <div className="chart-card-header">
                  <div>
                    <div className="chart-title">30-Day Forward Sales Demand Forecast (PyTorch LSTM)</div>
                    <div className="chart-subtitle">Projected sales volume with 95% Confidence Upper and Lower Bands</div>
                  </div>
                  {forecastBenchmarks && (
                    <div className="badge badge-success">
                      Champion: {forecastBenchmarks.champion_forecasting_model}
                    </div>
                  )}
                </div>
                <div className="chart-container" style={{ height: "360px" }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={futureForecast}>
                      <defs>
                        <linearGradient id="colorFc" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                          <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="forecast_date" stroke="#9ca3af" fontSize={11} />
                      <YAxis stroke="#9ca3af" fontSize={11} />
                      <Tooltip contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151" }} />
                      <Legend />
                      <Area type="monotone" dataKey="upper_confidence_bound" name="Upper 95% Band" stroke="#38bdf8" strokeDasharray="3 3" fill="none" />
                      <Area type="monotone" dataKey="predicted_sales" name="Predicted Demand ($)" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#colorFc)" />
                      <Area type="monotone" dataKey="lower_confidence_bound" name="Lower 95% Band" stroke="#38bdf8" strokeDasharray="3 3" fill="none" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Model Comparison Benchmark Table */}
              {forecastBenchmarks?.comparison_benchmarks && (
                <div className="table-card">
                  <div className="chart-card-header">
                    <div>
                      <div className="chart-title">Model Evaluation Benchmark (Deep Learning vs Statistical Baselines)</div>
                      <div className="chart-subtitle">Comparison across RMSE, MAE, and MAPE % on held-out evaluation horizon</div>
                    </div>
                  </div>
                  <div className="table-responsive">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Model Architecture</th>
                          <th>RMSE ($)</th>
                          <th>MAE ($)</th>
                          <th>MAPE (%)</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(forecastBenchmarks.comparison_benchmarks).map(([modelName, stats], idx) => (
                          <tr key={idx}>
                            <td style={{ fontWeight: 600 }}>{modelName}</td>
                            <td>${stats.rmse?.toLocaleString()}</td>
                            <td>${stats.mae?.toLocaleString()}</td>
                            <td>{stats.mape_pct}%</td>
                            <td>
                              <span className={`badge ${modelName === forecastBenchmarks.champion_forecasting_model ? "badge-success" : "badge-info"}`}>
                                {modelName === forecastBenchmarks.champion_forecasting_model ? "CHAMPION" : "BASELINE"}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ========================================================================= */}
          {/* TAB 7: ALERTS & DATA QUALITY                                              */}
          {/* ========================================================================= */}
          {activeTab === "alerts" && (
            <div className="page-body" style={{ padding: 0 }}>
              <div className="charts-grid">
                <div className="table-card">
                  <div className="chart-card-header">
                    <div>
                      <div className="chart-title">Automated Data Quality Audit Logs</div>
                      <div className="chart-subtitle">Evaluation of Completeness, Validity, Uniqueness & Consistency</div>
                    </div>
                  </div>
                  <div className="table-responsive">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Check</th>
                          <th>Quality Score</th>
                          <th>Completeness</th>
                          <th>Validity</th>
                          <th>Uniqueness</th>
                          <th>Consistency</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dataQualityLogs.map((log, idx) => (
                          <tr key={idx}>
                            <td style={{ fontWeight: 600 }}>{log.check_name}</td>
                            <td>
                              <span className="badge badge-success">{log.overall_quality_score}%</span>
                            </td>
                            <td>{log.completeness_score}%</td>
                            <td>{log.validity_score}%</td>
                            <td>{log.uniqueness_score}%</td>
                            <td>{log.consistency_score}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="table-card">
                  <div className="chart-card-header">
                    <div>
                      <div className="chart-title">Isolation Forest Anomaly Triggers</div>
                      <div className="chart-subtitle">Statistical outliers detected in daily business metrics</div>
                    </div>
                  </div>
                  <div className="table-responsive">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Metric</th>
                          <th>Current Value</th>
                          <th>Severity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {anomalies.map((anom, idx) => (
                          <tr key={idx}>
                            <td>{anom.alert_date}</td>
                            <td style={{ fontWeight: 600 }}>{anom.metric_name}</td>
                            <td>{Number(anom.current_value).toFixed(1)}</td>
                            <td>
                              <span className={`badge ${anom.severity === "Critical" ? "badge-critical" : "badge-warning"}`}>
                                {anom.severity}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* TAB 8: MODEL MONITORING & EXPLAINABILITY                                   */}
          {/* ========================================================================= */}
          {activeTab === "models" && (
            <div className="page-body" style={{ padding: 0 }}>
              {modelDrift && (
                <div className="kpi-grid">
                  <div className="kpi-card">
                    <div className="kpi-title">Model Status</div>
                    <div className="kpi-value" style={{ color: "var(--accent-emerald)" }}>
                      {modelDrift.overall_status}
                    </div>
                    <div className="kpi-trend">Version: {modelDrift.model_version}</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-title">Prediction PSI</div>
                    <div className="kpi-value">{modelDrift.prediction_psi}</div>
                    <div className="kpi-trend">Threshold: {modelDrift.drift_threshold} (No Drift)</div>
                  </div>
                  <div className="kpi-card">
                    <div className="kpi-title">High Churn Share</div>
                    <div className="kpi-value">{modelDrift.prediction_summary?.high_risk_share_pct}%</div>
                    <div className="kpi-trend">Mean Churn: {modelDrift.prediction_summary?.mean_churn_prob}</div>
                  </div>
                </div>
              )}

              {/* Feature Importance SHAP Chart */}
              <div className="chart-card full-width">
                <div className="chart-card-header">
                  <div>
                    <div className="chart-title">Customer Churn Model Feature Importance (Explainable AI)</div>
                    <div className="chart-subtitle">Primary drivers influencing customer attrition probability</div>
                  </div>
                </div>
                <div className="chart-container" style={{ height: "300px" }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={churnFeatureImportance} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis type="number" stroke="#9ca3af" fontSize={11} />
                      <YAxis dataKey="feature" type="category" stroke="#9ca3af" fontSize={11} width={160} />
                      <Tooltip contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151" }} />
                      <Bar dataKey="importance" fill="#6366f1" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* SQL Viewer Modal */}
      {activeSqlModal && (
        <div style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.75)", backdropFilter: "blur(4px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }}>
          <div style={{ background: "#111827", border: "1px solid #374151", borderRadius: "var(--radius-md)", width: "650px", maxWidth: "90%", padding: "24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 600 }}>
                <Code size={18} color="var(--accent-cyan)" />
                <span>Validated Read-Only SQL Query</span>
              </div>
              <button className="btn btn-secondary" style={{ padding: "4px 8px" }} onClick={() => setActiveSqlModal(null)}>
                Close
              </button>
            </div>
            <div className="sql-viewer-box">
              <pre>{activeSqlModal}</pre>
            </div>
            <div style={{ marginTop: "12px", fontSize: "0.75rem", color: "var(--text-muted)" }}>
              Executed with read-only database permissions. All DDL and DML operations are strictly blocked by the AST Validator.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
