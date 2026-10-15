-- ====================================================================
-- Enterprise AI Business Decision Intelligence Platform
-- Script 01: OLTP Relational Schema (PostgreSQL)
-- ====================================================================

-- 1. Suppliers Table
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_email VARCHAR(100),
    region VARCHAR(50),
    city VARCHAR(50),
    reliability_score NUMERIC(4,3) DEFAULT 1.000,
    lead_time_days INT DEFAULT 7,
    contract_status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_suppliers_region ON suppliers(region);

-- 2. Warehouses Table
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    region VARCHAR(50),
    capacity_sqft INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_warehouses_region ON warehouses(region);

-- 3. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    retail_price NUMERIC(12,2) NOT NULL CHECK (retail_price >= 0),
    cost_price NUMERIC(12,2) NOT NULL CHECK (cost_price >= 0),
    target_margin NUMERIC(5,4),
    supplier_id VARCHAR(50) REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    weight_kg NUMERIC(6,2),
    return_propensity NUMERIC(4,3) DEFAULT 0.05,
    reorder_point INT DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_subcategory ON products(subcategory);
CREATE INDEX IF NOT EXISTS idx_products_supplier ON products(supplier_id);

-- 4. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(30),
    gender VARCHAR(20),
    age INT CHECK (age >= 18 AND age <= 120),
    region VARCHAR(50),
    city VARCHAR(50),
    persona VARCHAR(50),
    expected_basket NUMERIC(10,2),
    order_freq_weight NUMERIC(4,2),
    signup_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_customers_region ON customers(region);
CREATE INDEX IF NOT EXISTS idx_customers_city ON customers(city);
CREATE INDEX IF NOT EXISTS idx_customers_signup ON customers(signup_date);

-- 5. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    order_date DATE NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0),
    discount_amount NUMERIC(10,2) DEFAULT 0.00,
    shipping_fee NUMERIC(8,2) DEFAULT 0.00,
    warehouse_id VARCHAR(50) REFERENCES warehouses(warehouse_id),
    delivery_days INT DEFAULT 3,
    status VARCHAR(50) DEFAULT 'Delivered',
    region VARCHAR(50),
    city VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_region ON orders(region);

-- 6. Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    unit_cost NUMERIC(12,2) NOT NULL CHECK (unit_cost >= 0),
    discount_amount NUMERIC(10,2) DEFAULT 0.00,
    total_amount NUMERIC(12,2) NOT NULL,
    profit_amount NUMERIC(12,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);

-- 7. Payments Table
CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL,
    amount NUMERIC(12,2) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'Success',
    payment_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date);

-- 8. Returns Table
CREATE TABLE IF NOT EXISTS returns (
    return_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    return_date DATE NOT NULL,
    reason VARCHAR(200),
    refund_amount NUMERIC(12,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Approved',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_returns_order ON returns(order_id);
CREATE INDEX IF NOT EXISTS idx_returns_product ON returns(product_id);
CREATE INDEX IF NOT EXISTS idx_returns_customer ON returns(customer_id);

-- 9. Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(order_id) ON DELETE SET NULL,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id),
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    sentiment VARCHAR(20),
    topic VARCHAR(100),
    review_text TEXT,
    review_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_customer ON reviews(customer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment);

-- 10. Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    warehouse_id VARCHAR(50) NOT NULL REFERENCES warehouses(warehouse_id),
    current_stock INT NOT NULL CHECK (current_stock >= 0),
    safety_stock INT DEFAULT 100,
    reorder_level INT DEFAULT 150,
    recommended_reorder_qty INT DEFAULT 0,
    last_restocked_date DATE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_warehouse ON inventory(warehouse_id);

-- 11. Marketing Campaigns Table
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_name VARCHAR(150) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    spend NUMERIC(12,2) NOT NULL,
    impressions INT DEFAULT 0,
    clicks INT DEFAULT 0,
    conversions INT DEFAULT 0,
    attributed_revenue NUMERIC(12,2) DEFAULT 0.00,
    roi NUMERIC(6,3) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_marketing_channel ON marketing_campaigns(channel);
CREATE INDEX IF NOT EXISTS idx_marketing_start ON marketing_campaigns(start_date);
