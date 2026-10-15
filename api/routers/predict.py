"""
ML & DL Real-Time Prediction API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter
from ml.churn import ChurnModelPipeline
from ml.returns import ReturnPredictionEngine
from dl.lstm_forecasting import DemandForecastingPipeline
from api.schemas import ChurnPredictionRequest, ReturnPredictionRequest, DemandPredictionRequest, StandardResponse

router = APIRouter(prefix="/api/predict", tags=["Real-Time ML Inferences"])
churn_pipeline = ChurnModelPipeline()
return_engine = ReturnPredictionEngine()
forecast_pipeline = DemandForecastingPipeline()

@router.post("/churn", response_model=StandardResponse)
def predict_customer_churn(req: ChurnPredictionRequest):
    """Predicts customer churn probability and key drivers using champion model"""
    features = req.model_dump()
    result = churn_pipeline.predict_single(features)
    return StandardResponse(success=True, data=result)

@router.post("/return", response_model=StandardResponse)
def predict_item_return(req: ReturnPredictionRequest):
    """Predicts item return risk based on category, delivery duration, and pricing"""
    features = req.model_dump()
    result = return_engine.predict_return_risk(features)
    return StandardResponse(success=True, data=result)

@router.post("/demand", response_model=StandardResponse)
def predict_sales_demand(req: DemandPredictionRequest):
    """Forecasts sales demand using PyTorch LSTM sequence model"""
    result = forecast_pipeline.generate_future_forecast(horizon_days=req.horizon_days)
    return StandardResponse(success=True, data=result)
