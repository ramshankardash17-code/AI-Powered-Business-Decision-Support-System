"""
Declarative Database Models (OLTP, Star Schema, Analytics & ML Storage)
Enterprise AI Business Decision Intelligence Platform
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from database.connection import Base

# ==========================================
# 1. OLTP LAYER (OPERATIONAL DATA STORE)
# ==========================================

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(String(50), primary_key=True)
    supplier_name = Column(String(150), nullable=False)
    contact_email = Column(String(100))
    region = Column(String(50), index=True)
    city = Column(String(50))
    reliability_score = Column(Float, default=1.0)
    lead_time_days = Column(Integer, default=7)
    contract_status = Column(String(20), default="Active")

    products = relationship("Product", back_populates="supplier")

class Warehouse(Base):
    __tablename__ = "warehouses"

    warehouse_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(50))
    region = Column(String(50), index=True)
    capacity_sqft = Column(Integer)

    orders = relationship("Order", back_populates="warehouse")
    inventory_items = relationship("Inventory", back_populates="warehouse")

class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), index=True, nullable=False)
    subcategory = Column(String(100), index=True)
    retail_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    target_margin = Column(Float)
    supplier_id = Column(String(50), ForeignKey("suppliers.supplier_id"))
    weight_kg = Column(Float)
    return_propensity = Column(Float, default=0.05)
    reorder_point = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)

    supplier = relationship("Supplier", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    inventory_records = relationship("Inventory", back_populates="product")

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(50), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(150), index=True)
    phone = Column(String(30))
    gender = Column(String(20))
    age = Column(Integer)
    region = Column(String(50), index=True)
    city = Column(String(50), index=True)
    persona = Column(String(50))
    expected_basket = Column(Float)
    order_freq_weight = Column(Float)
    signup_date = Column(Date, index=True)
    is_active = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), index=True)
    order_date = Column(Date, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    shipping_fee = Column(Float, default=0.0)
    warehouse_id = Column(String(50), ForeignKey("warehouses.warehouse_id"))
    delivery_days = Column(Integer, default=3)
    status = Column(String(50), index=True, default="Delivered")
    region = Column(String(50), index=True)
    city = Column(String(50))

    customer = relationship("Customer", back_populates="orders")
    warehouse = relationship("Warehouse", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")
    returns = relationship("Return", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey("orders.order_id"), index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    profit_amount = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey("orders.order_id"), index=True)
    payment_method = Column(String(50), index=True)
    amount = Column(Float, nullable=False)
    payment_status = Column(String(50), default="Success")
    payment_date = Column(Date, index=True)

    order = relationship("Order", back_populates="payments")

class Return(Base):
    __tablename__ = "returns"

    return_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey("orders.order_id"), index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), index=True)
    return_date = Column(Date, index=True)
    reason = Column(String(200))
    refund_amount = Column(Float, nullable=False)
    status = Column(String(50), default="Approved")

    order = relationship("Order", back_populates="returns")

class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey("orders.order_id"), index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), index=True)
    rating = Column(Integer, nullable=False)
    sentiment = Column(String(20), index=True)
    topic = Column(String(100), index=True)
    review_text = Column(Text)
    review_date = Column(Date, index=True)

    product = relationship("Product", back_populates="reviews")
    customer = relationship("Customer", back_populates="reviews")

class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(String(50), primary_key=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), index=True)
    warehouse_id = Column(String(50), ForeignKey("warehouses.warehouse_id"), index=True)
    current_stock = Column(Integer, nullable=False)
    safety_stock = Column(Integer, default=100)
    reorder_level = Column(Integer, default=150)
    recommended_reorder_qty = Column(Integer, default=0)
    last_restocked_date = Column(Date)

    product = relationship("Product", back_populates="inventory_records")
    warehouse = relationship("Warehouse", back_populates="inventory_items")

class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    campaign_id = Column(String(50), primary_key=True)
    campaign_name = Column(String(150), nullable=False)
    channel = Column(String(50), index=True)
    start_date = Column(Date, index=True)
    end_date = Column(Date)
    spend = Column(Float, nullable=False)
    impressions = Column(Integer)
    clicks = Column(Integer)
    conversions = Column(Integer)
    attributed_revenue = Column(Float)
    roi = Column(Float)


# ==========================================
# 2. STAR SCHEMA LAYER (DIMENSIONS & FACTS)
# ==========================================

class DimCustomer(Base):
    __tablename__ = "dim_customer"

    customer_key = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), unique=True, index=True)
    full_name = Column(String(200))
    email = Column(String(150))
    gender = Column(String(20))
    age_group = Column(String(50))
    region = Column(String(50), index=True)
    city = Column(String(50))
    signup_date = Column(Date)
    customer_segment = Column(String(50), default="Casual")

class DimProduct(Base):
    __tablename__ = "dim_product"

    product_key = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), unique=True, index=True)
    product_name = Column(String(200))
    category = Column(String(100), index=True)
    subcategory = Column(String(100), index=True)
    retail_price = Column(Float)
    cost_price = Column(Float)
    target_margin = Column(Float)
    supplier_id = Column(String(50))

class DimDate(Base):
    __tablename__ = "dim_date"

    date_key = Column(Integer, primary_key=True) # e.g. 20241015
    full_date = Column(Date, unique=True, index=True)
    day = Column(Integer)
    month = Column(Integer)
    month_name = Column(String(20))
    quarter = Column(Integer)
    year = Column(Integer, index=True)
    day_of_week = Column(Integer)
    day_name = Column(String(20))
    is_weekend = Column(Boolean)
    is_festive_season = Column(Boolean, default=False)

class DimLocation(Base):
    __tablename__ = "dim_location"

    location_key = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(100), index=True)
    region = Column(String(50), index=True)
    tier = Column(String(20))

class DimSupplier(Base):
    __tablename__ = "dim_supplier"

    supplier_key = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(String(50), unique=True, index=True)
    supplier_name = Column(String(150))
    region = Column(String(50))
    reliability_score = Column(Float)
    lead_time_days = Column(Integer)

class DimMarketingChannel(Base):
    __tablename__ = "dim_marketing_channel"

    channel_key = Column(Integer, primary_key=True, autoincrement=True)
    channel_name = Column(String(50), unique=True)
    channel_type = Column(String(50)) # Paid, Organic, Direct

class FactSales(Base):
    __tablename__ = "fact_sales"

    sales_key = Column(Integer, primary_key=True, autoincrement=True)
    order_item_id = Column(String(50), index=True)
    order_id = Column(String(50), index=True)
    date_key = Column(Integer, index=True)
    customer_id = Column(String(50), index=True)
    product_id = Column(String(50), index=True)
    region = Column(String(50), index=True)
    quantity = Column(Integer)
    gross_sales = Column(Float)
    discount_amount = Column(Float)
    net_sales = Column(Float)
    cogs = Column(Float)
    profit = Column(Float)
    profit_margin = Column(Float)

class FactOrders(Base):
    __tablename__ = "fact_orders"

    order_key = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), unique=True, index=True)
    date_key = Column(Integer, index=True)
    customer_id = Column(String(50), index=True)
    warehouse_id = Column(String(50))
    region = Column(String(50), index=True)
    total_amount = Column(Float)
    discount_amount = Column(Float)
    shipping_fee = Column(Float)
    delivery_days = Column(Integer)
    is_returned = Column(Boolean, default=False)
    status = Column(String(50))

class FactReturns(Base):
    __tablename__ = "fact_returns"

    return_key = Column(Integer, primary_key=True, autoincrement=True)
    return_id = Column(String(50), unique=True, index=True)
    order_id = Column(String(50), index=True)
    product_id = Column(String(50), index=True)
    customer_id = Column(String(50), index=True)
    date_key = Column(Integer, index=True)
    refund_amount = Column(Float)
    reason = Column(String(200))

class FactInventory(Base):
    __tablename__ = "fact_inventory"

    inventory_key = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(50), index=True)
    warehouse_id = Column(String(50), index=True)
    date_key = Column(Integer, index=True)
    current_stock = Column(Integer)
    safety_stock = Column(Integer)
    reorder_level = Column(Integer)
    is_stockout_risk = Column(Boolean, default=False)
    shortage_units = Column(Integer, default=0)

class FactMarketing(Base):
    __tablename__ = "fact_marketing"

    marketing_key = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(50), index=True)
    channel = Column(String(50), index=True)
    start_date_key = Column(Integer)
    spend = Column(Float)
    impressions = Column(Integer)
    clicks = Column(Integer)
    conversions = Column(Integer)
    attributed_revenue = Column(Float)
    roi = Column(Float)


# ==========================================
# 3. ANALYTICS & ML STORAGE LAYER
# ==========================================

class CustomerMLFeatures(Base):
    __tablename__ = "customer_ml_features"

    customer_id = Column(String(50), primary_key=True)
    recency_days = Column(Integer)
    frequency_orders = Column(Integer)
    monetary_total = Column(Float)
    avg_order_value = Column(Float)
    total_returns = Column(Integer)
    return_rate = Column(Float)
    avg_discount_rate = Column(Float)
    negative_reviews_count = Column(Integer)
    avg_delivery_delay = Column(Float)
    tenure_days = Column(Integer)
    rfm_segment = Column(String(50)) # Champions, Loyal, At Risk, Dormant, Discount Seekers
    churn_probability = Column(Float)
    churn_risk_level = Column(String(20)) # Low, Medium, High
    predicted_clv = Column(Float)
    is_high_value_high_churn = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"

    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), index=True) # e.g. "Electronics Return Rate", "Revenue Drop", "Stockout Risk"
    dimension = Column(String(100)) # e.g. "Category: Electronics"
    normal_value = Column(Float)
    current_value = Column(Float)
    deviation_pct = Column(Float)
    severity = Column(String(20)) # Low, Medium, High, Critical
    alert_date = Column(Date, index=True)
    description = Column(Text)
    status = Column(String(30), default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)

class DataQualityLog(Base):
    __tablename__ = "data_quality_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    check_name = Column(String(100))
    table_name = Column(String(100))
    completeness_score = Column(Float)
    validity_score = Column(Float)
    uniqueness_score = Column(Float)
    consistency_score = Column(Float)
    overall_quality_score = Column(Float)
    failed_rows_count = Column(Integer, default=0)
    details = Column(Text)
    evaluated_at = Column(DateTime, default=datetime.utcnow)

class ModelMonitoringLog(Base):
    __tablename__ = "model_monitoring_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), index=True)
    model_version = Column(String(50))
    metric_name = Column(String(50)) # ROC_AUC, F1, RMSE, PSI
    metric_value = Column(Float)
    drift_detected = Column(Boolean, default=False)
    psi_score = Column(Float, default=0.0)
    notes = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)
