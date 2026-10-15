"""
FastAPI Main Application Entrypoint
Enterprise AI Business Decision Intelligence Platform
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from database.connection import Base, engine, DB_DIALECT
from rag.vector_store import policy_vector_store
from api.routers import (
    kpi_router, sales_router, customers_router, inventory_router,
    marketing_router, forecast_router, alerts_router, models_router,
    agent_router, predict_router
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FastAPI_Server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Starting Enterprise Decision Intelligence API Service ===")
    logger.info(f"Target Database Dialect: {DB_DIALECT}")
    Base.metadata.create_all(bind=engine)
    policy_vector_store.load_and_index_documents()
    yield
    logger.info("=== Shutting down Enterprise Decision Intelligence API Service ===")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="Unified Enterprise AI Decision Intelligence Platform combining SQL Analytics, Machine Learning, Deep Learning Forecasting, RAG, and Agentic AI workflows.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Open for local dev and frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Modular Routers
app.include_router(kpi_router)
app.include_router(sales_router)
app.include_router(customers_router)
app.include_router(inventory_router)
app.include_router(marketing_router)
app.include_router(forecast_router)
app.include_router(alerts_router)
app.include_router(models_router)
app.include_router(agent_router)
app.include_router(predict_router)

@app.get("/health", tags=["System Health"])
def health_check():
    """Returns platform operational health and active database dialect"""
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "database_dialect": DB_DIALECT,
        "vector_chunks_indexed": len(policy_vector_store.chunks)
    }

@app.get("/", tags=["System Info"])
def root_info():
    """API Overview & Documentation Links"""
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "primary_features": [
            "Executive KPIs & Business Analytics",
            "Safe Text-to-SQL Engine with AST Validation",
            "Multi-Agent AI Decision Intelligence Assistant",
            "Customer Churn & CLV High-Value Risk Classifier",
            "PyTorch LSTM Demand Forecasting vs Baselines",
            "RAG Knowledge Engine for Enterprise SOPs",
            "Isolation Forest Anomaly & Stockout Diagnostics",
            "Model Monitoring & PSI Drift Detection"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
