# Corporate Business Intelligence Metric Definitions (MET-DEF-2024)

## 1. Top-Line Metrics
- **Gross Revenue**: Sum of all order item quantities multiplied by respective unit retail prices before discounts.
- **Net Revenue**: Gross Revenue minus promotional discounts plus shipping surcharges collected.
- **Cost of Goods Sold (COGS)**: Sum of order item quantities multiplied by respective unit cost prices from supplier contracts.
- **Gross Profit**: Net Revenue minus COGS.
- **Gross Profit Margin (%)**: `(Gross Profit / Net Revenue) * 100`.

## 2. Customer & Retention Metrics
- **Average Order Value (AOV)**: `Net Revenue / Total Distinct Orders`.
- **Churn Rate (%)**: Percentage of historical customers whose last completed order date exceeds 120 days or who exhibit model churn probability >= 70%.
- **Customer Lifetime Value (CLV)**: 12-month forward predictive spending derived from purchase frequency, margin contribution, and retention survival probability.

## 3. Operational & Supply Chain Metrics
- **Return Rate (%)**: `(Total Distinct Return Orders / Total Distinct Completed Orders) * 100`.
- **Stockout Rate (%)**: `(Number of SKUs with Physical Stock < Safety Stock) / Total Tracked Catalog SKUs * 100`.
- **Marketing ROI**: `(Attributed Revenue - Marketing Spend) / Marketing Spend`.
