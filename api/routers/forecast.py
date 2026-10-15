"""
Demand Forecasting API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter, Query
from dl.lstm_forecasting import DemandForecastingPipeline
from api.schemas import StandardResponse

router = APIRouter(prefix="/api/forecast", tags=["Demand Forecasting & Deep Learning"])
forecast_pipeline = DemandForecastingPipeline()

@router.get("/future", response_model=StandardResponse)
def get_future_demand_forecast(horizon_days: int = Query(30, ge=7, le=90)):
    """Generates 30-day future sales demand forecast using PyTorch LSTM with prediction intervals"""
    data = forecast_pipeline.generate_future_forecast(horizon_days=horizon_days)
    return StandardResponse(success=True, data=data)

@router.get("/benchmarks", response_model=StandardResponse)
def get_forecasting_benchmarks():
    """Returns comparative metrics (RMSE, MAE, MAPE) comparing LSTM vs Moving Averages vs Ridge"""
    data = forecast_pipeline.train_and_evaluate(epochs=15, test_days=30)
    return StandardResponse(success=True, data=data)
