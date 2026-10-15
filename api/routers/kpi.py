"""
KPI API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter
from analytics.kpi_engine import KPIEngine
from api.schemas import StandardResponse

router = APIRouter(prefix="/api/kpi", tags=["KPIs & Executive Summary"])
kpi_engine = KPIEngine()

@router.get("/summary", response_model=StandardResponse)
def get_executive_kpis():
    """Returns company-wide executive KPIs: Net Revenue, Profit, Margin, AOV, Churn, Return Rate"""
    data = kpi_engine.get_executive_summary()
    return StandardResponse(success=True, data=data)

@router.get("/time-series", response_model=StandardResponse)
def get_time_series_kpis():
    """Returns MoM, YoY, and rolling 3-month trends"""
    data = kpi_engine.get_time_series_metrics()
    return StandardResponse(success=True, data=data)
