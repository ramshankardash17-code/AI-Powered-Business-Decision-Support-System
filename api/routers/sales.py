"""
Sales & Revenue Analytics API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter
from analytics.kpi_engine import KPIEngine
from api.schemas import StandardResponse

router = APIRouter(prefix="/api/sales", tags=["Sales Analytics"])
kpi_engine = KPIEngine()

@router.get("/monthly-trend", response_model=StandardResponse)
def get_monthly_sales_trend():
    """Returns monthly revenue, profit, orders, and margin growth"""
    data = kpi_engine.get_time_series_metrics()
    return StandardResponse(success=True, data=data)

@router.get("/category-performance", response_model=StandardResponse)
def get_category_performance():
    """Returns sales breakdown, profit margin, and return rate per category"""
    data = kpi_engine.get_category_metrics()
    return StandardResponse(success=True, data=data)

@router.get("/regional-performance", response_model=StandardResponse)
def get_regional_performance():
    """Returns revenue, profit, orders, and delivery transit days by region"""
    data = kpi_engine.get_regional_metrics()
    return StandardResponse(success=True, data=data)
