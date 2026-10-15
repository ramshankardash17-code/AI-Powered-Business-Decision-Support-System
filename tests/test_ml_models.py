"""
Machine Learning & Forecasting Unit Tests
Enterprise AI Business Decision Intelligence Platform
"""
import pytest
from ml.churn import ChurnModelPipeline
from ml.returns import ReturnPredictionEngine
from ml.clv import CustomerLifetimeValueEngine

def test_churn_model_training_and_inference():
    pipeline = ChurnModelPipeline()
    res = pipeline.train_and_compare()
    assert "candidate_evaluations" in res
    assert "champion_model" in res
    assert res["best_roc_auc"] > 0.50

    sample_cust = {
        "recency_days": 180,
        "frequency_orders": 2,
        "monetary_total": 4500.0,
        "avg_order_value": 2250.0,
        "total_returns": 1,
        "return_rate": 0.5,
        "avg_discount_rate": 0.2,
        "negative_reviews_count": 2,
        "avg_delivery_delay": 8.0,
        "tenure_days": 200
    }
    pred = pipeline.predict_single(sample_cust)
    assert "churn_probability" in pred
    assert 0.0 <= pred["churn_probability"] <= 1.0
    assert pred["churn_risk_level"] in ["Low", "Medium", "High"]

def test_clv_model_execution():
    clv_engine = CustomerLifetimeValueEngine()
    data = clv_engine.train_and_predict()
    assert "total_high_value_high_churn_customers" in data
    assert data["high_value_clv_threshold"] > 0

def test_return_prediction():
    ret_engine = ReturnPredictionEngine()
    sample_item = {
        "category": "Electronics",
        "unit_price": 25000.0,
        "discount_amount": 1500.0,
        "delivery_days": 7,
        "customer_return_history": 0.25
    }
    res = ret_engine.predict_return_risk(sample_item)
    assert "return_probability" in res
    assert 0.0 <= res["return_probability"] <= 1.0
    assert res["risk_category"] in ["Low", "Medium", "High"]
