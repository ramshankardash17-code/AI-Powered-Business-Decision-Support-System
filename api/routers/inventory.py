"""
Inventory & Supply Chain API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter
from analytics.inventory_intelligence import InventoryIntelligenceEngine
from api.schemas import StandardResponse

router = APIRouter(prefix="/api/inventory", tags=["Inventory Intelligence"])
inv_engine = InventoryIntelligenceEngine()

@router.get("/health", response_model=StandardResponse)
def get_inventory_health():
    """Returns SKU-level stock, 30-day predicted demand, shortage, and reorder quantities"""
    data = inv_engine.evaluate_inventory_health()
    return StandardResponse(success=True, data=data)

@router.get("/stockout-summary", response_model=StandardResponse)
def get_stockout_summary():
    """Returns high-priority stockout warnings and total capital replenishment requirements"""
    data = inv_engine.get_stockout_summary()
    return StandardResponse(success=True, data=data)
