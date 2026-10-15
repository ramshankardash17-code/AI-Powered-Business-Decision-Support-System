# Power BI Enterprise Analytics Architecture & Dashboard Specification
**Platform**: Enterprise AI Business Decision Intelligence Platform  
**Target Roles**: Business Analyst, Data Analyst, BI Architect, Analytics Engineer  
**Data Model**: Star Schema (Kimball Methodology) with 6 Dimensions and 5 Fact Tables  

---

## 1. Dimensional Model & Relationships (Data Model View)

```
        +-------------------+           +-----------------------+
        |   dim_customer    |           |      dim_product      |
        |-------------------|           |-----------------------|
        | *customer_id (PK) |           | *product_id (PK)      |
        | full_name         |           | product_name          |
        | region, city      |           | category, subcategory |
        | rfm_segment       |           | retail_price, cost    |
        +---------+---------+           +-----------+-----------+
                  |                                 |
                  | 1                               | 1
                  |                                 |
                  | *                               | *
        +---------+---------------------------------+-----------+
        |                       fact_sales                      |
        |-------------------------------------------------------|
        | *order_item_id (PK)                                   |
        | order_id, date_key, customer_id, product_id, region   |
        | quantity, gross_sales, discount_amount, net_sales     |
        | cogs, profit, profit_margin                           |
        +---------+---------------------------------+-----------+
                  | *                               | *
                  |                                 |
                  | 1                               | 1
        +---------+---------+           +-----------+-----------+
        |     dim_date      |           |     dim_location      |
        |-------------------|           |-----------------------|
        | *date_key (PK)    |           | *location_key (PK)    |
        | full_date, month  |           | city, region, tier    |
        | quarter, year     |           +-----------------------+
        | is_festive_season |
        +-------------------+
```

### Table Relationships in Power BI
1. `dim_date[date_key]` 1 : * `fact_sales[date_key]` (Active, Single direction)
2. `dim_customer[customer_id]` 1 : * `fact_sales[customer_id]` (Active, Single direction)
3. `dim_product[product_id]` 1 : * `fact_sales[product_id]` (Active, Single direction)
4. `dim_product[product_id]` 1 : * `fact_inventory[product_id]` (Active, Single direction)
5. `dim_customer[customer_id]` 1 : * `fact_orders[customer_id]` (Active, Single direction)
6. `dim_customer[customer_id]` 1 : 1 `customer_ml_features[customer_id]` (Active, Both directions)

---

## 2. Core DAX Measures Specification (DAX Measure Table: `_Measures`)

### A. Sales & Financial Measures
```dax
-- Total Net Revenue
Total Revenue = SUM(fact_sales[net_sales])

-- Total Gross Revenue
Gross Revenue = SUM(fact_sales[gross_sales])

-- Total Cost of Goods Sold
Total COGS = SUM(fact_sales[cogs])

-- Total Gross Profit
Total Profit = SUM(fact_sales[profit])

-- Profit Margin %
Profit Margin % = 
DIVIDE([Total Profit], [Total Revenue], 0) * 100

-- Total Units Sold
Total Units Sold = SUM(fact_sales[quantity])

-- Total Orders
Total Orders = DISTINCTCOUNT(fact_sales[order_id])

-- Average Order Value (AOV)
Average Order Value = 
DIVIDE([Total Revenue], [Total Orders], 0)
```

### B. Time Intelligence DAX Measures
```dax
-- Previous Month Revenue
Revenue PM = 
CALCULATE([Total Revenue], PREVIOUSMONTH(dim_date[full_date]))

-- Month-over-Month Revenue Growth %
Revenue MoM % = 
VAR PrevRev = [Revenue PM]
RETURN 
    IF(ISBLANK(PrevRev), BLANK(), DIVIDE([Total Revenue] - PrevRev, PrevRev, 0) * 100)

-- Previous Year Revenue (YoY)
Revenue PY = 
CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[full_date]))

-- Year-over-Year Revenue Growth %
Revenue YoY % = 
VAR PrevYearRev = [Revenue PY]
RETURN 
    IF(ISBLANK(PrevYearRev), BLANK(), DIVIDE([Total Revenue] - PrevYearRev, PrevYearRev, 0) * 100)

-- Rolling 30-Day Revenue
Revenue 30D Rolling = 
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(dim_date[full_date], LASTDATE(dim_date[full_date]), -30, DAY)
)
```

### C. Customer & Retention DAX Measures
```dax
-- Total Active Customers
Active Customers = DISTINCTCOUNT(fact_sales[customer_id])

-- Churn Rate %
Churn Rate % = 
VAR ChurnedCusts = CALCULATE(COUNTROWS(customer_ml_features), customer_ml_features[churn_risk_level] = "High")
VAR TotalCusts = COUNTROWS(customer_ml_features)
RETURN DIVIDE(ChurnedCusts, TotalCusts, 0) * 100

-- High Value High Churn Customers Count
High Value High Churn Customers = 
CALCULATE(
    COUNTROWS(customer_ml_features),
    customer_ml_features[is_high_value_high_churn] = TRUE()
)

-- High Value CLV at Risk ($)
High Value CLV at Risk = 
CALCULATE(
    SUM(customer_ml_features[predicted_clv]),
    customer_ml_features[is_high_value_high_churn] = TRUE()
)

-- Return Rate %
Return Rate % = 
VAR TotalReturns = DISTINCTCOUNT(fact_returns[return_id])
RETURN DIVIDE(TotalReturns, [Total Orders], 0) * 100
```

### D. Inventory & Supply Chain DAX Measures
```dax
-- Total Current Inventory Stock
Current Inventory Stock = SUM(fact_inventory[current_stock])

-- Stockout Ratio %
Stockout Ratio % = 
VAR RiskItems = CALCULATE(COUNTROWS(fact_inventory), fact_inventory[is_stockout_risk] = TRUE())
VAR TotalItems = COUNTROWS(fact_inventory)
RETURN DIVIDE(RiskItems, TotalItems, 0) * 100

-- Total Units Shortage
Total Shortage Units = SUM(fact_inventory[shortage_units])
```

### E. Marketing & Acquisition DAX Measures
```dax
-- Total Marketing Spend
Total Marketing Spend = SUM(fact_marketing[spend])

-- Attributed Marketing Revenue
Marketing Revenue = SUM(fact_marketing[attributed_revenue])

-- Marketing ROI (Blended)
Blended Marketing ROI = 
DIVIDE([Marketing Revenue] - [Total Marketing Spend], [Total Marketing Spend], 0)

-- Blended Customer Acquisition Cost (CAC)
Blended CAC = 
VAR TotalConversions = SUM(fact_marketing[conversions])
RETURN DIVIDE([Total Marketing Spend], TotalConversions, 0)
```

---

## 3. Power BI 10-Page Dashboard Layout Specification

### PAGE 1: Executive Overview
- **Header**: Enterprise Decision Intelligence Platform | Executive Summary
- **KPI Cards Row**: Total Net Revenue ($), Gross Profit ($), Profit Margin (%), Total Orders, Active Customers, Blended Return Rate (%).
- **Visual 1 (Line & Clustered Column Chart)**: Monthly Revenue vs Profit Trend with Margin % secondary axis.
- **Visual 2 (Donut Chart)**: Revenue Breakdown by Product Category.
- **Visual 3 (Filled Map / Bar Chart)**: Net Revenue & Delivery Lead Times across Geographical Sales Regions.
- **Visual 4 (Alert Card / Table)**: Live Anomaly Alerts (Return rate surges, stockout warnings).

### PAGE 2: Sales Analytics
- **Visual 1 (Area Chart)**: Day-over-Day & Week-over-Week Cumulative Sales Velocity.
- **Visual 2 (Matrix Table)**: Category & Subcategory breakdown (Gross Sales, Discounts, Net Sales, COGS, Profit, Margin %).
- **Visual 3 (Scatter Plot)**: Discount % vs Sales Volume (Price Elasticity Analysis).
- **Slicers**: Year, Quarter, Region, Product Category.

### PAGE 3: Customer Analytics
- **Visual 1 (Treemap)**: Customer Distribution across RFM Segments (Champions, High Value Loyalists, Potential Loyalists, Discount Seekers, At Risk).
- **Visual 2 (Bar Chart)**: Average Order Value & Purchase Frequency by Age Group and Gender.
- **Visual 3 (Table)**: Top 50 Most Valuable Customers with Recent Activity dates and Lifetime Value.

### PAGE 4: Product Analytics
- **Visual 1 (Tornado / Bar Chart)**: Top 10 Most Profitable vs Top 10 Least Profitable Products.
- **Visual 2 (Heatmap Matrix)**: Product Category vs Return Reasons (Defective, Sizing, Delivery Delay, Misrepresented).
- **Visual 3 (Scatter Plot)**: Product Retail Price vs Return Propensity.

### PAGE 5: Marketing Analytics
- **Visual 1 (Funnel Chart)**: Impressions -> Clicks -> Conversions -> Attributed Orders.
- **Visual 2 (Column Chart)**: Marketing Spend vs Attributed Revenue per Channel (Google, Meta, Email, Influencer, Affiliate).
- **Visual 3 (Card + Gauge)**: Channel ROI vs Target Benchmark (3.0x).

### PAGE 6: Inventory & Supply Chain
- **Visual 1 (Card Matrix)**: Critical Shortage SKUs, Healthy SKUs, Total Reorder Capital Required ($).
- **Visual 2 (Gantt / Bar Chart)**: Current Stock vs Safety Stock per Warehouse Hub (Mumbai, Delhi, Bengaluru, Kolkata, Indore).
- **Visual 3 (Table with Data Bars)**: Recommended Reorder Quantities with Supplier Lead Times.

### PAGE 7: Churn and CLV Prediction
- **Visual 1 (Quadrant 2x2 Scatter)**: Predicted CLV (Y-Axis) vs Churn Probability (X-Axis). Highlight upper-right quadrant as "URGENT INTERVENTION".
- **Visual 2 (Gauge)**: Total High-Value CLV at Stake ($).
- **Visual 3 (Action Table)**: Action List of High-Value High-Risk Customers with Suggested Retention Incentives.

### PAGE 8: Demand Forecasting (Deep Learning vs Baselines)
- **Visual 1 (Line Chart with Bands)**: Historical Sales (Solid Blue), PyTorch LSTM 30-Day Forecast (Dashed Green), 95% Confidence Interval Upper/Lower Bands (Light Shaded Area).
- **Visual 2 (Grouped Column Chart)**: Model Error Benchmark: LSTM vs Ridge Regression vs Moving Averages (RMSE, MAE, MAPE).

### PAGE 9: Data Quality Governance
- **Visual 1 (Radial Gauge)**: Overall Enterprise Data Quality Score (Target: > 85.0%).
- **Visual 2 (Bar Chart)**: 4-Pillar Quality Breakdown: Completeness %, Validity %, Uniqueness %, Consistency %.
- **Visual 3 (Audit Log Table)**: Automated Ingestion Test History with Failed Row Counts.

### PAGE 10: ML Model Monitoring & Drift
- **Visual 1 (Line Chart)**: Churn Model Prediction Population Stability Index (PSI) over Time.
- **Visual 2 (Heatmap)**: Feature Drift KS-Test Statistics for Key Input Variables (Recency, Monetary, Returns).
- **Visual 3 (Status Badge)**: Champion Model Version (`v2.1.0-prod`) and Deployment Timestamp.

---

## 4. Power Query (M-Code) Connection Template

```powerquery
let
    // PostgreSQL Source Connection
    Source = Value.NativeQuery(
        PostgreSQL.Database("localhost", "ecommerce_bi"),
        "SELECT * FROM vw_executive_kpis",
        null,
        [EnableFolding=true]
    )
in
    Source
```
