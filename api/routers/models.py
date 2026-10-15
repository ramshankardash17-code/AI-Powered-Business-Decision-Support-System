"""
Model Monitoring & Explainability API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter
from ml.monitoring import ModelMonitoringEngine
from ml.churn import ChurnModelPipeline
from api.schemas import StandardResponse

router = APIRouter(prefix="/api/models", tags=["Model Monitoring & Explainability"])
monitor = ModelMonitoringEngine()
churn_pipeline = ChurnModelPipeline()

@router.get("/monitoring/drift", response_model=StandardResponse)
def get_model_drift_audit():
    """Returns Population Stability Index (PSI) and Kolmogorov-Smirnov feature drift tests"""
    audit = monitor.evaluate_churn_model_drift()
    return StandardResponse(success=True, data=audit)

@router.get("/monitoring/logs", response_model=StandardResponse)
def get_monitoring_logs():
    """Returns historical model evaluation and drift log entries"""
    logs = monitor.get_monitoring_history()
    return StandardResponse(success=True, data=logs)

@router.get("/explainability/churn", response_model=StandardResponse)
def get_churn_feature_importance():
    """Returns SHAP / global feature importance drivers for customer churn model"""
    eval_res = churn_pipeline.train_and_compare()
    return StandardResponse(success=True, data=eval_res)
