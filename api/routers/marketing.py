"""
Marketing Analytics API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter
from analytics.kpi_engine import KPIEngine
from api.schemas import StandardResponse

router = APIRouter(prefix="/api/marketing", tags=["Marketing & Campaigns"])
kpi_engine = KPIEngine()

@router.get("/roi", response_model=StandardResponse)
def get_marketing_roi():
    """Returns spend, impressions, clicks, conversions, and ROI by marketing channel"""
    data = kpi_engine.get_marketing_roi()
    return StandardResponse(success=True, data=data)
