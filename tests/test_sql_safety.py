"""
SQL Safety & AST Validation Unit Tests
Enterprise AI Business Decision Intelligence Platform
"""
import pytest
from agents.text_to_sql import SafeTextToSQLEngine

@pytest.fixture
def sql_engine():
    return SafeTextToSQLEngine()

def test_sql_blocks_dangerous_ddl(sql_engine):
    dangerous_queries = [
        "DROP TABLE customers;",
        "DELETE FROM orders WHERE 1=1;",
        "TRUNCATE TABLE fact_sales;",
        "ALTER TABLE products ADD COLUMN hacked TEXT;",
        "UPDATE customer_ml_features SET churn_probability = 0;"
    ]
    for q in dangerous_queries:
        is_valid, msg = sql_engine.validate_sql(q)
        assert is_valid is False, f"Expected dangerous query '{q}' to be blocked"

def test_sql_allows_read_only_select(sql_engine):
    safe_queries = [
        "SELECT * FROM fact_sales LIMIT 10;",
        "SELECT category, SUM(net_sales) FROM fact_sales GROUP BY category;",
        "WITH cte AS (SELECT * FROM dim_customer) SELECT COUNT(*) FROM cte;"
    ]
    for q in safe_queries:
        is_valid, msg = sql_engine.validate_sql(q)
        assert is_valid is True, f"Expected safe query '{q}' to be approved, got: {msg}"

def test_natural_language_to_sql_execution(sql_engine):
    res = sql_engine.natural_language_to_sql("Show me top 10 products by profit in South")
    assert res["success"] is True
    assert "sql" in res
    assert "data" in res
    assert len(res["data"]) <= 10
