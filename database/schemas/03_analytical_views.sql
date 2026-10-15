-- ====================================================================
-- Enterprise AI Business Decision Intelligence Platform
-- Script 03: Analytical Views for Power BI & Business Intelligence
-- ====================================================================

-- 1. Executive KPIs Summary View
CREATE OR REPLACE VIEW vw_executive_kpis AS
SELECT
    COUNT(DISTINCT fs.order_id) AS total_orders,
    COUNT(DISTINCT fs.customer_id) AS total_customers,
    SUM(fs.quantity) AS total_units_sold,
    ROUND(SUM(fs.gross_sales), 2) AS gross_revenue,
    ROUND(SUM(fs.discount_amount), 2) AS total_discounts,
    ROUND(SUM(fs.net_sales), 2) AS net_revenue,
    ROUND(SUM(fs.cogs), 2) AS total_cogs,
    ROUND(SUM(fs.profit), 2) AS total_profit,
    ROUND((SUM(fs.profit) / NULLIF(SUM(fs.net_sales), 0)) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(fs.net_sales) / NULLIF(COUNT(DISTINCT fs.order_id), 0), 2) AS avg_order_value
FROM fact_sales fs;

-- 2. Monthly Revenue and Profit Trend View
CREATE OR REPLACE VIEW vw_monthly_trend AS
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(DISTINCT fs.order_id) AS orders_count,
    ROUND(SUM(fs.net_sales), 2) AS monthly_revenue,
    ROUND(SUM(fs.profit), 2) AS monthly_profit,
    ROUND((SUM(fs.profit) / NULLIF(SUM(fs.net_sales), 0)) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(fs.net_sales), 2) AS avg_item_revenue
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;

-- 3. Category Performance & Return Rate View
CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    dp.category,
    COUNT(DISTINCT fs.order_id) AS orders_count,
    SUM(fs.quantity) AS units_sold,
    ROUND(SUM(fs.net_sales), 2) AS net_revenue,
    ROUND(SUM(fs.profit), 2) AS total_profit,
    ROUND((SUM(fs.profit) / NULLIF(SUM(fs.net_sales), 0)) * 100, 2) AS profit_margin_pct,
    ROUND(COALESCE(SUM(fr.refund_amount), 0), 2) AS returned_amount,
    ROUND((COUNT(DISTINCT fr.return_id)::NUMERIC / NULLIF(COUNT(DISTINCT fs.order_item_id), 0)) * 100, 2) AS return_rate_pct
FROM fact_sales fs
JOIN dim_product dp ON fs.product_id = dp.product_id
LEFT JOIN fact_returns fr ON fs.order_id = fr.order_id AND fs.product_id = fr.product_id
GROUP BY dp.category
ORDER BY net_revenue DESC;

-- 4. Regional Performance View
CREATE OR REPLACE VIEW vw_regional_performance AS
SELECT
    fs.region,
    COUNT(DISTINCT fs.order_id) AS orders_count,
    COUNT(DISTINCT fs.customer_id) AS active_customers,
    ROUND(SUM(fs.net_sales), 2) AS net_revenue,
    ROUND(SUM(fs.profit), 2) AS total_profit,
    ROUND((SUM(fs.profit) / NULLIF(SUM(fs.net_sales), 0)) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(fo.delivery_days), 1) AS avg_delivery_days
FROM fact_sales fs
LEFT JOIN fact_orders fo ON fs.order_id = fo.order_id
GROUP BY fs.region
ORDER BY net_revenue DESC;

-- 5. Product Stockout Risk & Shortage View
CREATE OR REPLACE VIEW vw_product_stockout_risk AS
SELECT
    dp.product_id,
    dp.product_name,
    dp.category,
    dp.retail_price,
    fi.warehouse_id,
    fi.current_stock,
    fi.safety_stock,
    fi.reorder_level,
    CASE 
        WHEN fi.current_stock < fi.safety_stock THEN 'Critical Shortage'
        WHEN fi.current_stock < fi.reorder_level THEN 'Reorder Required'
        ELSE 'Healthy Stock'
    END AS stock_health_status,
    GREATEST(0, (fi.safety_stock * 2) - fi.current_stock) AS recommended_reorder_qty
FROM fact_inventory fi
JOIN dim_product dp ON fi.product_id = dp.product_id
ORDER BY fi.current_stock ASC;

-- 6. Customer RFM & Churn Risk View
CREATE OR REPLACE VIEW vw_customer_risk_summary AS
SELECT
    cmf.customer_id,
    dc.full_name,
    dc.region,
    dc.city,
    cmf.rfm_segment,
    cmf.monetary_total,
    cmf.frequency_orders,
    cmf.recency_days,
    ROUND(cmf.churn_probability::NUMERIC, 3) AS churn_probability,
    cmf.churn_risk_level,
    ROUND(cmf.predicted_clv::NUMERIC, 2) AS predicted_clv,
    cmf.is_high_value_high_churn
FROM customer_ml_features cmf
JOIN dim_customer dc ON cmf.customer_id = dc.customer_id
ORDER BY cmf.churn_probability DESC;
