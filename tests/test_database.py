"""
Database & Star Schema Unit Tests
Enterprise AI Business Decision Intelligence Platform
"""
import pytest
from sqlalchemy import text
from database.connection import engine, execute_raw_sql

def test_database_connection():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1 AS test_val")).fetchone()
        assert res[0] == 1

def test_star_schema_tables_exist():
    required_tables = [
        "fact_sales", "fact_orders", "fact_returns", "fact_inventory", "fact_marketing",
        "dim_customer", "dim_product", "dim_date", "customer_ml_features"
    ]
    with engine.connect() as conn:
        for tbl in required_tables:
            query = text(f"SELECT COUNT(*) FROM {tbl};")
            count = conn.execute(query).scalar()
            assert count >= 0, f"Table {tbl} should be queryable"

def test_executive_kpi_query():
    sql = "SELECT COUNT(DISTINCT order_id) AS orders, SUM(net_sales) AS sales FROM fact_sales;"
    rows = execute_raw_sql(sql)
    assert len(rows) > 0
    assert rows[0]["orders"] > 0
