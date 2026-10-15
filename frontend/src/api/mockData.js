/**
 * Enterprise AI Decision Support System - Precomputed High-Fidelity Demo Data
 * Mirrors PostgreSQL Star Schema & Multi-Agent Intelligence Engines
 */

export const mockKPIs = {
  total_orders: 56712,
  total_customers: 14850,
  net_revenue: 8421950.0,
  gross_revenue: 9680400.0,
  total_discounts: 1258450.0,
  total_cogs: 6799150.0,
  total_profit: 1622800.0,
  profit_margin_pct: 19.27,
  avg_order_value: 148.51,
  total_returns: 3412,
  return_rate_pct: 6.02,
  total_items_tracked: 480,
  stockout_risk_items: 4,
  stockout_rate_pct: 0.83,
  churn_rate_pct: 14.54,
  data_quality_score: 98.4
};

export const mockTimeSeries = [
  { metric: "Net Revenue", current_period: 724800, previous_period: 791400, mom_pct: -8.42, yoy_pct: 12.4 },
  { metric: "Gross Profit", current_period: 139160, previous_period: 151950, mom_pct: -8.42, yoy_pct: 9.1 },
  { metric: "Profit Margin", current_period: 19.2, previous_period: 21.4, mom_pct: -2.2, yoy_pct: -0.6 },
  { metric: "Order Volume", current_period: 4890, previous_period: 5120, mom_pct: -4.49, yoy_pct: 14.8 },
  { metric: "Return Rate", current_period: 7.8, previous_period: 5.6, mom_pct: 2.2, yoy_pct: 1.4 },
  { metric: "High-Risk Churn Accounts", current_period: 216, previous_period: 182, mom_pct: 18.68, yoy_pct: 15.2 }
];

export const mockMonthlySales = [
  { month_name: "Jan 2024", revenue: 580000, profit: 121000, orders: 4100, margin_pct: 20.8 },
  { month_name: "Feb 2024", revenue: 610000, profit: 132000, orders: 4250, margin_pct: 21.6 },
  { month_name: "Mar 2024", revenue: 690000, profit: 152000, orders: 4700, margin_pct: 22.0 },
  { month_name: "Apr 2024", revenue: 640000, profit: 138000, orders: 4400, margin_pct: 21.5 },
  { month_name: "May 2024", revenue: 710000, profit: 158000, orders: 4900, margin_pct: 22.2 },
  { month_name: "Jun 2024", revenue: 730000, profit: 161000, orders: 5050, margin_pct: 22.0 },
  { month_name: "Jul 2024", revenue: 680000, profit: 147000, orders: 4600, margin_pct: 21.6 },
  { month_name: "Aug 2024", revenue: 750000, profit: 168000, orders: 5150, margin_pct: 22.4 },
  { month_name: "Sep 2024", revenue: 791400, profit: 174000, orders: 5400, margin_pct: 22.0 },
  { month_name: "Oct 2024", revenue: 724800, profit: 139160, orders: 4890, margin_pct: 19.2 },
  { month_name: "Nov 2024 (Fc)", revenue: 840000, profit: 182000, orders: 5800, margin_pct: 21.6 },
  { month_name: "Dec 2024 (Fc)", revenue: 990000, profit: 218000, orders: 6800, margin_pct: 22.0 }
];

export const mockCategories = [
  { category: "Electronics", revenue: 3450000, profit: 621000, margin_pct: 18.0, orders: 19200 },
  { category: "Home & Kitchen", revenue: 1980000, profit: 435600, margin_pct: 22.0, orders: 14100 },
  { category: "Apparel & Shoes", revenue: 1420000, profit: 340800, margin_pct: 24.0, orders: 11500 },
  { category: "Beauty & Personal", revenue: 890000, profit: 240300, margin_pct: 27.0, orders: 6800 },
  { category: "Sports & Fitness", revenue: 681950, profit: 149900, margin_pct: 22.0, orders: 5112 }
];

export const mockRegions = [
  { region: "North", revenue: 2650000, profit: 543000, orders: 17400, return_rate: 5.4 },
  { region: "South", revenue: 2210000, profit: 382000, orders: 14800, return_rate: 7.9 },
  { region: "West", revenue: 2140000, profit: 472000, orders: 14100, return_rate: 5.1 },
  { region: "East", revenue: 1421950, profit: 312000, orders: 10412, return_rate: 5.8 }
];

export const mockCustomerSegments = [
  { segment_name: "Champions (High CLV, High Recency)", customer_count: 2450, avg_monetary: 1840, churn_risk_pct: 4.2 },
  { segment_name: "Loyal Customers", customer_count: 4120, avg_monetary: 920, churn_risk_pct: 9.8 },
  { segment_name: "Potential Loyalists", customer_count: 3600, avg_monetary: 460, churn_risk_pct: 16.4 },
  { segment_name: "At-Risk (High Value)", customer_count: 1820, avg_monetary: 1250, churn_risk_pct: 48.6 },
  { segment_name: "High-Churn Immediate Risk", customer_count: 216, avg_monetary: 6712, churn_risk_pct: 86.4 },
  { segment_name: "Hibernating / Lost", customer_count: 2644, avg_monetary: 180, churn_risk_pct: 92.1 }
];

export const mockHighRiskCustomers = {
  total_high_value_high_churn_customers: 216,
  high_risk_clv_at_stake: 1450000,
  top_at_risk_list: [
    { customer_id: "CUST-8812", name: "Apex Retail Systems", clv: 28400, churn_probability: 0.89, last_order_days: 64, complaints: 4 },
    { customer_id: "CUST-4109", name: "Vanguard Tech Corp", clv: 24150, churn_probability: 0.86, last_order_days: 58, complaints: 3 },
    { customer_id: "CUST-7721", name: "Horizon Enterprise", clv: 21900, churn_probability: 0.84, last_order_days: 72, complaints: 2 },
    { customer_id: "CUST-1044", name: "OmniSupply Logistics", clv: 19800, churn_probability: 0.81, last_order_days: 49, complaints: 3 },
    { customer_id: "CUST-6320", name: "Summit Health Group", clv: 18400, churn_probability: 0.79, last_order_days: 62, complaints: 2 }
  ]
};

export const mockInventoryHealth = [
  { product_name: "HyperView 4K Smart OLED (Product X)", category: "Electronics", current_stock: 12, safety_stock: 100, is_stockout_risk: true, days_of_inventory: 1.8 },
  { product_name: "QuantumSound Pro ANC Headphones", category: "Electronics", current_stock: 24, safety_stock: 80, is_stockout_risk: true, days_of_inventory: 2.4 },
  { product_name: "UltraBreeze Smart Air Purifier", category: "Home & Kitchen", current_stock: 35, safety_stock: 75, is_stockout_risk: true, days_of_inventory: 3.1 },
  { product_name: "RoboVac Precision Laser LiDAR", category: "Home & Kitchen", current_stock: 18, safety_stock: 60, is_stockout_risk: true, days_of_inventory: 2.2 },
  { product_name: "AeroForm Ergonomic Mesh Chair", category: "Home & Kitchen", current_stock: 180, safety_stock: 50, is_stockout_risk: false, days_of_inventory: 18.5 },
  { product_name: "ProFitness Dual Pulse Treadmill", category: "Sports & Fitness", current_stock: 140, safety_stock: 40, is_stockout_risk: false, days_of_inventory: 21.0 }
];

export const mockStockoutSummary = {
  total_skus: 480,
  critical_stockouts: 4,
  stockout_risk_rate_pct: 0.83,
  estimated_revenue_at_risk: 148500,
  affected_warehouses: ["South Central (Dallas)", "East Coast (Newark)"]
};

export const mockForecastBenchmarks = {
  champion_forecasting_model: "PyTorch 2-Layer LSTM Sequence Forecaster",
  sequence_window_days: 30,
  lstm_metrics: {
    rmse: 24120,
    mae: 19040,
    mape_pct: 14.5,
    r2_score: 0.892
  },
  comparison_table: [
    { model: "PyTorch LSTM (Champion)", rmse: 24120, mae: 19040, mape_pct: 14.5, type: "Deep Learning" },
    { model: "Ridge Lag Regression", rmse: 31050, mae: 24200, mape_pct: 18.2, type: "ML Baseline" },
    { model: "7-Day Rolling Average", rmse: 38400, mae: 29500, mape_pct: 22.4, type: "Time-Series Baseline" },
    { model: "30-Day Moving Average", rmse: 44100, mae: 35200, mape_pct: 27.1, type: "Statistical Mean" }
  ]
};

export const mockFutureForecast = Array.from({ length: 30 }, (_, i) => {
  const date = new Date(2024, 10, i + 1);
  const dateStr = date.toISOString().split("T")[0];
  const dayOfWeek = date.getDay();
  const weekendBoost = dayOfWeek === 0 || dayOfWeek === 6 ? 6000 : 0;
  const trend = i * 280;
  const base = 24500 + weekendBoost + trend;
  return {
    forecast_date: dateStr,
    predicted_sales: Math.round(base),
    lower_bound: Math.round(base * 0.88),
    upper_bound: Math.round(base * 1.12)
  };
});

export const mockAnomalies = [
  {
    anomaly_id: "ANOM-2024-104",
    metric_name: "Gross Profit Contraction",
    detected_at: "2024-10-14 08:30:00",
    severity: "CRITICAL",
    score: 0.94,
    description: "Gross Profit dropped -8.4% MoM driven by Electronics margin compression and severe stockouts in South DC."
  },
  {
    anomaly_id: "ANOM-2024-102",
    metric_name: "Return Rate Surge on Electronics",
    detected_at: "2024-10-12 14:15:00",
    severity: "HIGH",
    score: 0.82,
    description: "Returns on audio and visual goods spiked to 11.8% (+4.2% above control limit) due to carrier delivery damages."
  },
  {
    anomaly_id: "ANOM-2024-098",
    metric_name: "Inventory Safety Stock Breach",
    detected_at: "2024-10-10 11:00:00",
    severity: "HIGH",
    score: 0.88,
    description: "HyperView 4K OLED stock fell below 15 units (safety threshold: 100 units). 14-day stockout trajectory predicted."
  }
];

export const mockDataQualityLogs = [
  { check_name: "Completeness: Fact Sales & Order Items", status: "PASSED", score_pct: 100.0, details: "0 missing primary or foreign keys across 56,712 transactions", audited_at: "2024-10-15 00:00:00" },
  { check_name: "Validity: Sales Pricing & Discount Rules", status: "PASSED", score_pct: 99.8, details: "Discounts strictly constrained within 0% to 50% range", audited_at: "2024-10-15 00:00:00" },
  { check_name: "Uniqueness: Customer Dimensional Keys", status: "PASSED", score_pct: 100.0, details: "14,850 distinct customer hashes verified", audited_at: "2024-10-15 00:00:00" },
  { check_name: "Consistency: COGS vs Unit Margin Validation", status: "PASSED", score_pct: 99.4, details: "Unit margin logic validated against supplier catalog", audited_at: "2024-10-15 00:00:00" }
];

export const mockModelDrift = {
  feature_drift_detected: false,
  psi_score: 0.042,
  ks_statistic: 0.038,
  status: "Healthy (Within Threshold < 0.15)",
  monitored_features: [
    { feature: "recency_days", psi: 0.035, drift: false },
    { feature: "avg_order_value", psi: 0.048, drift: false },
    { feature: "return_rate", psi: 0.062, drift: false },
    { feature: "negative_reviews_count", psi: 0.071, drift: false }
  ]
};

export const mockChurnExplainability = {
  champion_model: "XGBoost Classifier (ROC-AUC: 0.884, F1-Score: 0.826)",
  feature_importance: [
    { feature: "recency_days", importance: 0.312 },
    { feature: "return_rate", importance: 0.224 },
    { feature: "avg_delivery_delay", importance: 0.178 },
    { feature: "negative_reviews_count", importance: 0.142 },
    { feature: "avg_discount_rate", importance: 0.082 },
    { feature: "monetary_total", importance: 0.062 }
  ]
};

/**
 * Intelligent Multi-Agent Query Resolver for Standalone / Demo Mode
 */
export function resolveAgentQuery(question) {
  const q = question.toLowerCase();

  // 1. Root Cause / Profit Decline / Decision inquiry
  if (q.includes("why") || q.includes("profit") || q.includes("decrease") || q.includes("decline") || q.includes("drop")) {
    return {
      question,
      plan: ["planner_agent", "sql_agent", "root_cause_agent", "ml_churn_agent", "inventory_agent", "rag_policy_agent", "insight_agent"],
      audit_trail: [
        { agent: "Planner Agent", action: "Parsed intent: Root-cause variance decomposition & executive action playbook" },
        { agent: "SQL Agent", action: "Executed AST-validated SQL query on fact_sales joined with dim_product and dim_date" },
        { agent: "Root Cause Agent", action: "Isolated 64.2% of contraction to Electronics category ($148,200 absolute variance)" },
        { agent: "Inventory Agent", action: "Detected severe stockout on flagship SKU 'HyperView 4K Smart OLED' (12 units vs 100 safety stock)" },
        { agent: "ML Churn Agent", action: "Flagged 216 High-Value accounts at risk of churn ($1.45M CLV at immediate stake)" },
        { agent: "RAG Agent", action: "Retrieved verified clauses from SOP-RET-2024-V3 and SOP-INV-2024-V2" },
        { agent: "Insight Agent", action: "Synthesized multi-agent findings into verified enterprise decision schema" }
      ],
      executive_summary: "Profit contracted by 8.4% in the recent monthly reporting cycle ($148,200 absolute variance). Primary root cause analysis isolates 64.2% of the decline to the Electronics category, heavily driven by inventory stockouts on flagship SKU 'HyperView 4K Smart OLED (Product X)'. Concurrently, 216 high-value tier customers are flagged at imminent risk of churn due to unresolved delivery delays, representing $1,450,000 in endangered Customer Lifetime Value.",
      evidence: [
        "Statistical profit change: -8.4% period-over-period.",
        "Largest category profit drop: Electronics (-18.2% contraction).",
        "Critical warehouse stockouts: 4 SKUs operating below minimum safety threshold.",
        "High-Value + High-Churn accounts flagged: 216 customers ($1.45M CLV at stake)."
      ],
      important_kpis: {
        profit_pct_change: -8.4,
        top_declining_category: "Electronics",
        high_value_churn_customers: 216,
        clv_at_stake: 1450000,
        critical_stockout_skus: 4
      },
      root_cause_analysis: [
        {
          dimension: "Product & Inventory",
          type: "Stockout Surge",
          severity: "CRITICAL",
          finding: "Product X (HyperView 4K Smart OLED) experienced 14 stockout days in South & Central distribution centers, creating $94,500 in unfulfilled backorders."
        },
        {
          dimension: "Category Margin",
          type: "Discount Erosion",
          severity: "HIGH",
          finding: "Aggressive promotional discounting in Electronics eroded gross margins from 24.1% to 17.8% without generating offsetting unit volume."
        },
        {
          dimension: "Logistics & Churn",
          type: "Carrier Delay Impact",
          severity: "HIGH",
          finding: "Average delivery delay surged to 4.2 days across Regional Hub 3, causing a 38% increase in return requests and negative CSAT reviews."
        }
      ],
      forecast: null,
      chart_data: {
        chart_type: "bar",
        x_key: "category",
        y_key: "profit_change",
        series: [
          { category: "Electronics", profit_change: -18.2 },
          { category: "Home & Kitchen", profit_change: -4.1 },
          { category: "Apparel", profit_change: 3.8 },
          { category: "Beauty", profit_change: 7.2 },
          { category: "Sports", profit_change: 1.4 }
        ]
      },
      recommendations: [
        {
          action: "Trigger Emergency Purchase Order (PO-4481)",
          detail: "Expedite shipment of 600 units of HyperView OLED from secondary supplier TechFlow to restore safety stock within 48 hours.",
          requires_approval: true
        },
        {
          action: "Execute VIP Customer Retention Campaign",
          detail: "Dispatch automated apology email with $25 account credit to all 216 delayed High-Value customers per SOP-RET-2024-V3.",
          requires_approval: true
        },
        {
          action: "Enforce Electronics Promotional Floor",
          detail: "Cap maximum promotional discount rate at 12% across high-margin subcategories to prevent further margin erosion.",
          requires_approval: false
        }
      ],
      sources: [
        "fact_sales", "fact_orders", "fact_inventory", "dim_product",
        "customer_ml_features", "01_return_and_refund_policy.md", "02_inventory_procurement_sop.md"
      ],
      sql_used: "SELECT dp.category, ROUND(SUM(fs.profit), 2) AS current_profit, ROUND((SUM(fs.profit) - LAG(SUM(fs.profit)) OVER (PARTITION BY dp.category ORDER BY dd.year, dd.month)) / NULLIF(LAG(SUM(fs.profit)) OVER (PARTITION BY dp.category ORDER BY dd.year, dd.month), 0) * 100, 2) AS profit_change_pct FROM fact_sales fs JOIN dim_product dp ON fs.product_key = dp.product_key JOIN dim_date dd ON fs.date_key = dd.date_key GROUP BY dp.category, dd.year, dd.month HAVING dd.year = 2024 AND dd.month = 10;",
      models_used: [
        "XGBoost Customer Churn Classifier (v2.1)",
        "PyTorch LSTM Demand Forecaster",
        "Isolation Forest Anomaly Detector",
        "Safe Text-to-SQL AST Validator",
        "Policy Vector Store (TF-IDF / Cosine)"
      ],
      suggested_follow_up: [
        "Which customers are at risk and what should we do?",
        "What will sales look like next month?",
        "What does our return policy say about electronics?",
        "Show the top 10 products by profit in South"
      ]
    };
  }

  // 2. Churn / Customer ML inquiry
  if (q.includes("customer") || q.includes("risk") || q.includes("churn") || q.includes("retention") || q.includes("clv")) {
    return {
      question,
      plan: ["planner_agent", "ml_churn_agent", "insight_agent"],
      audit_trail: [
        { agent: "Planner Agent", action: "Identified customer retention and machine learning intent" },
        { agent: "ML Churn Agent", action: "Queried XGBoost Classifier inference outputs and RFM cluster metrics" },
        { agent: "Insight Agent", action: "Synthesized customer cohort risk segmentation" }
      ],
      executive_summary: "The XGBoost customer churn model flagged 216 Tier-1 enterprise accounts in the 'High-Value + High-Risk' quadrant. Total Customer Lifetime Value at immediate risk is $1,450,000. Primary churn drivers identified via SHAP values are recency days > 45, delivery delays exceeding 4 days, and repeated return interactions.",
      evidence: [
        "216 High-Value accounts exhibiting churn probability > 75%.",
        "Average CLV per endangered customer: $6,712.",
        "Top SHAP feature drivers: recency_days (31.2%), return_rate (22.4%), avg_delivery_delay (17.8%)."
      ],
      important_kpis: {
        high_value_churn_count: 216,
        endangered_clv: 1450000,
        model_roc_auc: 0.884
      },
      root_cause_analysis: [
        {
          dimension: "Fulfillment",
          type: "Shipping Delay",
          severity: "HIGH",
          finding: "78% of the at-risk customers placed orders routed through Regional Hub 3 during carrier backlog weeks."
        }
      ],
      forecast: null,
      chart_data: {
        chart_type: "bar",
        x_key: "segment",
        y_key: "risk_score",
        series: [
          { segment: "Tier 1 High-Risk", risk_score: 86.4 },
          { segment: "Tier 2 Mid-Risk", risk_score: 48.6 },
          { segment: "Tier 3 Moderate", risk_score: 16.4 },
          { segment: "Champions", risk_score: 4.2 }
        ]
      },
      recommendations: [
        {
          action: "Deploy Proactive Retention Outreach",
          detail: "Assign dedicated account managers to contact the top 25 high-CLV at-risk accounts within 24 hours.",
          requires_approval: true
        },
        {
          action: "Automate Goodwill Credit Playbook",
          detail: "Trigger automated $25 credits to accounts experiencing delivery delays > 3 days per SOP-RET-2024-V3.",
          requires_approval: false
        }
      ],
      sources: ["customer_ml_features", "dim_customer", "04_customer_retention_and_churn_policy.md"],
      sql_used: "SELECT customer_id, recency_days, frequency_orders, monetary_total, churn_probability FROM customer_ml_features WHERE churn_probability > 0.70 ORDER BY monetary_total DESC LIMIT 20;",
      models_used: ["XGBoost Classifier", "K-Means RFM Segmentation Engine", "SHAP TreeExplainer"],
      suggested_follow_up: [
        "Why did profit decrease last month?",
        "What will sales look like next month?",
        "What does our return policy say about electronics?"
      ]
    };
  }

  // 3. Forecast / Next month demand inquiry
  if (q.includes("forecast") || q.includes("next month") || q.includes("future") || q.includes("predict")) {
    const series = mockFutureForecast.slice(0, 15);
    return {
      question,
      plan: ["planner_agent", "forecast_agent", "insight_agent"],
      audit_trail: [
        { agent: "Planner Agent", action: "Identified deep learning sequence forecasting intent" },
        { agent: "Forecast Agent", action: "Executed 2-layer PyTorch LSTM model with 30-day lookback sequence" },
        { agent: "Insight Agent", action: "Assembled benchmark comparison and projected demand curves" }
      ],
      executive_summary: "Demand forecast generated using the champion PyTorch 2-layer LSTM sequence model across a 30-day forward horizon. Daily sales are projected to average $28,450, representing an 8.6% month-over-month volume expansion driven by holiday seasonality.",
      evidence: [
        "Model Architecture: 2-layer LSTM with 64 hidden units, dropout, and Dense head.",
        "Model Performance: 14.5% MAPE and $24,120 RMSE, outperforming baseline 30-day moving average ($44,100 RMSE).",
        "Projected 30-day total sales volume: ~$853,500."
      ],
      important_kpis: {
        projected_daily_avg: 28450,
        horizon_days: 30,
        lstm_mape_pct: 14.5
      },
      root_cause_analysis: [],
      forecast: series,
      chart_data: {
        chart_type: "line",
        x_key: "forecast_date",
        y_key: "predicted_sales",
        series
      },
      recommendations: [
        {
          action: "Pre-order High-Demand SKU Inventory",
          detail: "Increase buffer stock on Electronics and Home Goods by 15% ahead of forecasted day 18-24 volume spikes.",
          requires_approval: true
        }
      ],
      sources: ["fact_sales", "dim_date", "lstm_demand_forecaster.pt"],
      sql_used: "SELECT date, SUM(net_sales) AS daily_revenue FROM fact_sales GROUP BY date ORDER BY date DESC LIMIT 90;",
      models_used: ["PyTorch LSTM Sequence Model", "Ridge Exogenous Regression", "7-Day Rolling Baseline"],
      suggested_follow_up: [
        "Why did profit decrease last month?",
        "Which products have stockout risk next month?",
        "Show the top 10 products by profit in South"
      ]
    };
  }

  // 4. Policy / RAG / SOP inquiry
  if (q.includes("policy") || q.includes("return") || q.includes("sop") || q.includes("refund") || q.includes("electronics")) {
    return {
      question,
      plan: ["planner_agent", "rag_policy_agent", "insight_agent"],
      audit_trail: [
        { agent: "Planner Agent", action: "Identified policy lookup intent" },
        { agent: "RAG Agent", action: "Executed TF-IDF vector similarity search against corporate governance repository" },
        { agent: "Insight Agent", action: "Extracted verified policy clauses with document citations" }
      ],
      executive_summary: "Grounded retrieval from SOP-RET-2024-V3 (§3.2 Electronics & High-Value Items): The standard return window for Electronics is strictly 14 days from delivery (compared to 30 days for general merchandise). All returned electronic goods must include original packaging and serial numbers. Opened non-defective items are subject to a mandatory 15% restocking fee.",
      evidence: [
        "SOP-RET-2024-V3 §3.2: 14-day cutoff strictly enforced on TV/Audio/Computing products.",
        "SOP-RET-2024-V3 §4.1: Automated return portal flags items exceeding 14 days for supervisor review.",
        "SOP-RET-2024-V3 §5.3: Verified defective units within 30 days receive instant replacement or full credit."
      ],
      important_kpis: {
        electronics_return_window_days: 14,
        restocking_fee_pct: 15,
        citation_confidence_pct: 97.4
      },
      root_cause_analysis: [],
      forecast: null,
      chart_data: null,
      recommendations: [
        {
          action: "Audit Return Portal Automated Cutoffs",
          detail: "Verify the web customer portal programmatically blocks RMA requests for electronics delivered > 14 days ago.",
          requires_approval: false
        }
      ],
      sources: ["01_return_and_refund_policy.md", "03_pricing_and_discount_rules.md"],
      sql_used: null,
      models_used: ["TF-IDF / Cosine Vector Retriever", "RAG Grounded Extractor"],
      suggested_follow_up: [
        "Why did profit decrease last month?",
        "Which products have return rate above 10%?",
        "Which customers are at risk and what should we do?"
      ]
    };
  }

  // 5. Default / Regional / SQL query
  return {
    question,
    plan: ["planner_agent", "sql_agent", "insight_agent"],
    audit_trail: [
      { agent: "Planner Agent", action: "Parsed natural language query into SQL specification" },
      { agent: "SQL Agent", action: "Generated AST-safe read-only SQL for Star Schema fact and dimension tables" },
      { agent: "Insight Agent", action: "Formatted result set into visualization series" }
    ],
    executive_summary: "Safe Text-to-SQL query executed successfully against Star Schema. AST parser validated read-only permissions and rejected all DDL/DML vectors. Top profit contributors identified across regional dimension.",
    evidence: [
      "Top product: QuantumSound Pro ANC Headphones ($142,800 profit).",
      "Total profit generated by top cohort: $482,500.",
      "Query executed in 8ms with zero hallucination."
    ],
    important_kpis: {
      rows_retrieved: 10,
      execution_ms: 8
    },
    root_cause_analysis: [],
    forecast: null,
    chart_data: {
      chart_type: "bar",
      x_key: "product_name",
      y_key: "profit",
      series: [
        { product_name: "QuantumSound Pro", profit: 142800 },
        { product_name: "HyperView OLED", profit: 118400 },
        { product_name: "RoboVac Precision", profit: 89200 },
        { product_name: "UltraBreeze Purifier", profit: 74600 },
        { product_name: "AeroForm Chair", profit: 57500 }
      ]
    },
    recommendations: [
      {
        action: "Focus Regional Ad Spend on High-Margin SKUs",
        detail: "Allocate 60% of South regional digital marketing budget to top-tier performers with > 22% margin.",
        requires_approval: false
      }
    ],
    sources: ["fact_sales", "dim_product", "dim_geography"],
    sql_used: "SELECT dp.product_name, SUM(fs.profit) AS profit FROM fact_sales fs JOIN dim_product dp ON fs.product_key = dp.product_key JOIN dim_geography dg ON fs.geography_key = dg.geography_key WHERE dg.region = 'South' GROUP BY dp.product_name ORDER BY profit DESC LIMIT 10;",
    models_used: ["Safe Text-to-SQL AST Validator"],
    suggested_follow_up: [
      "Why did profit decrease last month?",
      "Which customers are at risk and what should we do?",
      "What will sales look like next month?"
    ]
  };
}
