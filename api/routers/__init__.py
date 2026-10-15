from .kpi import router as kpi_router
from .sales import router as sales_router
from .customers import router as customers_router
from .inventory import router as inventory_router
from .marketing import router as marketing_router
from .forecast import router as forecast_router
from .alerts import router as alerts_router
from .models import router as models_router
from .agent import router as agent_router
from .predict import router as predict_router

__all__ = [
    "kpi_router",
    "sales_router",
    "customers_router",
    "inventory_router",
    "marketing_router",
    "forecast_router",
    "alerts_router",
    "models_router",
    "agent_router",
    "predict_router"
]
