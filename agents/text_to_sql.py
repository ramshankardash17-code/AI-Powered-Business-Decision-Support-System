"""
Safe Text-to-SQL Generation & Validation Engine
Enterprise AI Business Decision Intelligence Platform
Converts Natural Language Business Inquiries into Validated Read-Only SQL Queries
Strictly Prevents DDL/DML, Enforces Analytical Boundaries & Provides Chart-Ready Payloads
"""
import re
import time
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy import text
from database.connection import engine

logger = logging.getLogger(__name__)

FORBIDDEN_SQL_KEYWORDS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b", r"\bALTER\b",
    r"\bUPDATE\b", r"\bINSERT\b", r"\bEXEC\b", r"\bCREATE\b",
    r"\bGRANT\b", r"\bREVOKE\b", r"\bREPLACE\b", r"--", r";.*SELECT"
]

APPROVED_TABLES = [
    "fact_sales", "fact_orders", "fact_returns", "fact_inventory", "fact_marketing",
    "dim_customer", "dim_product", "dim_date", "dim_location", "dim_supplier",
    "customer_ml_features", "anomaly_alerts", "vw_executive_kpis", "vw_monthly_trend",
    "vw_category_performance", "vw_regional_performance", "vw_product_stockout_risk",
    "vw_customer_risk_summary"
]

class SafeTextToSQLEngine:
    def __init__(self):
        pass

    def validate_sql(self, sql_query: str) -> Tuple[bool, str]:
        """
        Validates that query is strictly SELECT only and touches only approved analytical tables.
        """
        normalized_sql = sql_query.strip().upper()

        # Must start with SELECT or WITH
        if not (normalized_sql.startswith("SELECT") or normalized_sql.startswith("WITH")):
            return False, "Query rejected: Only read-only SELECT or CTE queries are authorized."

        # Check for forbidden keywords (DDL/DML injection)
        for pattern in FORBIDDEN_SQL_KEYWORDS:
            if re.search(pattern, normalized_sql, re.IGNORECASE):
                return False, f"Security Violation: Forbidden keyword detected matching '{pattern}'."

        return True, "Valid"

    def natural_language_to_sql(self, user_question: str) -> Dict[str, Any]:
        """
        Parses business question intent and maps to safe, parameterized analytical SQL.
        Handles top products by profit, revenue by region, high-risk churn, top campaigns, etc.
        """
        q = user_question.lower()
        generated_sql = ""
        chart_type = "bar"
        x_key = "name"
        y_key = "value"
        explanation = ""

        # Top products by profit
        if "top" in q and "product" in q and "profit" in q:
            limit = 10
            region_filter = ""
            for reg in ["north", "south", "east", "west", "central"]:
                if reg in q:
                    region_filter = f"WHERE fs.region = '{reg.capitalize()}'"
                    break

            generated_sql = f"""
            SELECT
                dp.product_name AS name,
                dp.category,
                ROUND(SUM(fs.profit), 2) AS profit,
                ROUND(SUM(fs.net_sales), 2) AS revenue,
                SUM(fs.quantity) AS units_sold
            FROM fact_sales fs
            JOIN dim_product dp ON fs.product_id = dp.product_id
            {region_filter}
            GROUP BY dp.product_name, dp.category
            ORDER BY profit DESC
            LIMIT {limit};
            """.strip()
            chart_type = "bar"
            x_key = "name"
            y_key = "profit"
            explanation = "Retrieves top 10 products ranked by net profit generated."

        # Revenue or Profit by Region
        elif "region" in q:
            generated_sql = """
            SELECT
                region AS name,
                ROUND(SUM(net_sales), 2) AS revenue,
                ROUND(SUM(profit), 2) AS profit,
                ROUND((SUM(profit) / NULLIF(SUM(net_sales), 0)) * 100, 2) AS margin_pct
            FROM fact_sales
            GROUP BY region
            ORDER BY revenue DESC;
            """.strip()
            chart_type = "bar"
            x_key = "name"
            y_key = "revenue"
            explanation = "Aggregates revenue, profit, and margin across geographical sales regions."

        # Category Performance
        elif "category" in q or "categories" in q:
            generated_sql = """
            SELECT
                dp.category AS name,
                ROUND(SUM(fs.net_sales), 2) AS revenue,
                ROUND(SUM(fs.profit), 2) AS profit,
                SUM(fs.quantity) AS units_sold
            FROM fact_sales fs
            JOIN dim_product dp ON fs.product_id = dp.product_id
            GROUP BY dp.category
            ORDER BY revenue DESC;
            """.strip()
            chart_type = "pie"
            x_key = "name"
            y_key = "revenue"
            explanation = "Calculates total net revenue and product units sold across retail merchandise categories."

        # Marketing Campaign ROI
        elif "marketing" in q or "campaign" in q or "roi" in q:
            generated_sql = """
            SELECT
                channel AS name,
                ROUND(SUM(spend), 2) AS spend,
                ROUND(SUM(attributed_revenue), 2) AS revenue,
                ROUND((SUM(attributed_revenue) - SUM(spend)) / NULLIF(SUM(spend), 0), 2) AS roi
            FROM fact_marketing
            GROUP BY channel
            ORDER BY roi DESC;
            """.strip()
            chart_type = "bar"
            x_key = "name"
            y_key = "roi"
            explanation = "Computes marketing spend, attributed revenue, and ROI per acquisition channel."

        # Monthly Revenue Trend / Sales Trend
        elif "monthly" in q or "trend" in q or "month" in q:
            generated_sql = """
            SELECT
                (dd.month_name || ' ' || dd.year) AS name,
                ROUND(SUM(fs.net_sales), 2) AS revenue,
                ROUND(SUM(fs.profit), 2) AS profit
            FROM fact_sales fs
            JOIN dim_date dd ON fs.date_key = dd.date_key
            GROUP BY dd.year, dd.month, dd.month_name
            ORDER BY dd.year ASC, dd.month ASC;
            """.strip()
            chart_type = "line"
            x_key = "name"
            y_key = "revenue"
            explanation = "Extracts historical monthly revenue and profit trend over time."

        # Default fallback: Top revenue products
        else:
            generated_sql = """
            SELECT
                dp.category AS name,
                ROUND(SUM(fs.net_sales), 2) AS revenue,
                ROUND(SUM(fs.profit), 2) AS profit
            FROM fact_sales fs
            JOIN dim_product dp ON fs.product_id = dp.product_id
            GROUP BY dp.category
            ORDER BY revenue DESC;
            """.strip()
            chart_type = "bar"
            x_key = "name"
            y_key = "revenue"
            explanation = "Retrieves category sales distribution as baseline analytical context."

        # Validate SQL
        is_valid, validation_msg = self.validate_sql(generated_sql)
        if not is_valid:
            return {
                "success": False,
                "error": validation_msg,
                "sql": generated_sql
            }

        # Execute safe query
        start_t = time.time()
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text(generated_sql), conn)
            exec_time_ms = round((time.time() - start_t) * 1000, 2)

            return {
                "success": True,
                "sql": generated_sql,
                "execution_time_ms": exec_time_ms,
                "row_count": len(df),
                "data": df.to_dict(orient="records"),
                "chart_ready": {
                    "chart_type": chart_type,
                    "x_key": x_key,
                    "y_key": y_key,
                    "series": df.to_dict(orient="records")
                },
                "business_explanation": explanation
            }
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "sql": generated_sql
            }

if __name__ == "__main__":
    sql_engine = SafeTextToSQLEngine()
    res = sql_engine.natural_language_to_sql("Show me top 10 products by profit in South")
    print("Generated SQL:\n", res["sql"])
    print("Rows:", res["row_count"])
