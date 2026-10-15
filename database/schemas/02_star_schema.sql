-- ====================================================================
-- Enterprise AI Business Decision Intelligence Platform
-- Script 02: Dimensional Model / Star Schema (PostgreSQL)
-- ====================================================================

-- 1. Dim Customer
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    email VARCHAR(150),
    gender VARCHAR(20),
    age_group VARCHAR(50),
    region VARCHAR(50),
    city VARCHAR(50),
    signup_date DATE,
    customer_segment VARCHAR(50) DEFAULT 'Casual'
);
CREATE INDEX IF NOT EXISTS idx_dim_cust_region ON dim_customer(region);
CREATE INDEX IF NOT EXISTS idx_dim_cust_segment ON dim_customer(customer_segment);

-- 2. Dim Product
CREATE TABLE IF NOT EXISTS dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    retail_price NUMERIC(12,2),
    cost_price NUMERIC(12,2),
    target_margin NUMERIC(5,4),
    supplier_id VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS idx_dim_prod_cat ON dim_product(category);
CREATE INDEX IF NOT EXISTS idx_dim_prod_subcat ON dim_product(subcategory);

-- 3. Dim Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY, -- YYYYMMDD
    full_date DATE UNIQUE NOT NULL,
    day INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_festive_season BOOLEAN DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS idx_dim_date_year ON dim_date(year);
CREATE INDEX IF NOT EXISTS idx_dim_date_month ON dim_date(year, month);

-- 4. Dim Location
CREATE TABLE IF NOT EXISTS dim_location (
    location_key SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    tier VARCHAR(20)
);
CREATE INDEX IF NOT EXISTS idx_dim_loc_reg ON dim_location(region);

-- 5. Dim Supplier
CREATE TABLE IF NOT EXISTS dim_supplier (
    supplier_key SERIAL PRIMARY KEY,
    supplier_id VARCHAR(50) UNIQUE NOT NULL,
    supplier_name VARCHAR(150),
    region VARCHAR(50),
    reliability_score NUMERIC(4,3),
    lead_time_days INT
);

-- 6. Dim Marketing Channel
CREATE TABLE IF NOT EXISTS dim_marketing_channel (
    channel_key SERIAL PRIMARY KEY,
    channel_name VARCHAR(50) UNIQUE NOT NULL,
    channel_type VARCHAR(50)
);

-- 7. Fact Sales (Granularity: 1 row per order item)
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_key SERIAL PRIMARY KEY,
    order_item_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    date_key INT NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    quantity INT NOT NULL,
    gross_sales NUMERIC(12,2) NOT NULL,
    discount_amount NUMERIC(10,2) DEFAULT 0.00,
    net_sales NUMERIC(12,2) NOT NULL,
    cogs NUMERIC(12,2) NOT NULL,
    profit NUMERIC(12,2) NOT NULL,
    profit_margin NUMERIC(6,4) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fact_sales_date ON fact_sales(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_cust ON fact_sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_prod ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_reg ON fact_sales(region);

-- 8. Fact Orders (Granularity: 1 row per order)
CREATE TABLE IF NOT EXISTS fact_orders (
    order_key SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    date_key INT NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    warehouse_id VARCHAR(50),
    region VARCHAR(50),
    total_amount NUMERIC(12,2) NOT NULL,
    discount_amount NUMERIC(10,2) DEFAULT 0.00,
    shipping_fee NUMERIC(8,2) DEFAULT 0.00,
    delivery_days INT,
    is_returned BOOLEAN DEFAULT FALSE,
    status VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS idx_fact_orders_date ON fact_orders(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_orders_cust ON fact_orders(customer_id);

-- 9. Fact Returns
CREATE TABLE IF NOT EXISTS fact_returns (
    return_key SERIAL PRIMARY KEY,
    return_id VARCHAR(50) UNIQUE NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    date_key INT NOT NULL,
    refund_amount NUMERIC(12,2) NOT NULL,
    reason VARCHAR(200)
);
CREATE INDEX IF NOT EXISTS idx_fact_returns_date ON fact_returns(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_returns_prod ON fact_returns(product_id);

-- 10. Fact Inventory
CREATE TABLE IF NOT EXISTS fact_inventory (
    inventory_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    warehouse_id VARCHAR(50) NOT NULL,
    date_key INT NOT NULL,
    current_stock INT NOT NULL,
    safety_stock INT,
    reorder_level INT,
    is_stockout_risk BOOLEAN DEFAULT FALSE,
    shortage_units INT DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_fact_inv_prod ON fact_inventory(product_id);

-- 11. Fact Marketing
CREATE TABLE IF NOT EXISTS fact_marketing (
    marketing_key SERIAL PRIMARY KEY,
    campaign_id VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    start_date_key INT NOT NULL,
    spend NUMERIC(12,2) NOT NULL,
    impressions INT,
    clicks INT,
    conversions INT,
    attributed_revenue NUMERIC(12,2),
    roi NUMERIC(6,3)
);
CREATE INDEX IF NOT EXISTS idx_fact_mkt_channel ON fact_marketing(channel);
