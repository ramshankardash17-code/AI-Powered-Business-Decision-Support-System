"""
Customer Intelligence API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter
from sqlalchemy import text
from database.connection import engine
from ml.segmentation import CustomerSegmentationEngine
from ml.clv import CustomerLifetimeValueEngine
from api.schemas import StandardResponse

router = APIRouter(prefix="/api/customers", tags=["Customer Intelligence & Retention"])

@router.get("/segments", response_model=StandardResponse)
def get_customer_segments():
    """Returns RFM cluster statistics and customer distributions"""
    sql = """
    SELECT
        rfm_segment,
        COUNT(*) AS customer_count,
        ROUND(AVG(monetary_total), 2) AS avg_spend,
        ROUND(AVG(frequency_orders), 1) AS avg_orders,
        ROUND(AVG(recency_days), 0) AS avg_recency,
        ROUND(AVG(churn_probability) * 100, 1) AS avg_churn_pct
    FROM customer_ml_features
    GROUP BY rfm_segment
    ORDER BY avg_spend DESC;
    """
    with engine.connect() as conn:
        import pandas as pd
        df = pd.read_sql(text(sql), conn)
    return StandardResponse(success=True, data=df.to_dict(orient="records"))

@router.get("/high-value-high-risk", response_model=StandardResponse)
def get_high_value_churn_customers():
    """Returns VIP and High-CLV customers facing immediate churn risk"""
    clv_engine = CustomerLifetimeValueEngine()
    data = clv_engine.train_and_predict()
    return StandardResponse(success=True, data=data)

@router.get("/churn-risk-distribution", response_model=StandardResponse)
def get_churn_risk_distribution():
    """Returns distribution of Low, Medium, and High churn risk customers"""
    sql = """
    SELECT
        churn_risk_level,
        COUNT(*) AS customer_count,
        ROUND(AVG(predicted_clv), 2) AS avg_predicted_clv,
        ROUND(SUM(predicted_clv), 2) AS total_clv_at_risk
    FROM customer_ml_features
    GROUP BY churn_risk_level
    ORDER BY customer_count DESC;
    """
    with engine.connect() as conn:
        import pandas as pd
        df = pd.read_sql(text(sql), conn)
    return StandardResponse(success=True, data=df.to_dict(orient="records"))
