"""
Pydantic Schemas for API Requests & Responses
Enterprise AI Business Decision Intelligence Platform
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Prediction Requests
class ChurnPredictionRequest(BaseModel):
    recency_days: int = Field(..., description="Days since customer's last order", example=45)
    frequency_orders: int = Field(..., description="Total lifetime orders", example=6)
    monetary_total: float = Field(..., description="Total spending amount", example=24500.0)
    avg_order_value: float = Field(..., description="Average basket size", example=4083.33)
    total_returns: int = Field(0, description="Total returns initiated", example=1)
    return_rate: float = Field(0.0, description="Returns divided by orders", example=0.16)
    avg_discount_rate: float = Field(0.0, description="Average discount rate", example=0.10)
    negative_reviews_count: int = Field(0, description="Count of negative reviews", example=1)
    avg_delivery_delay: float = Field(3.0, description="Average delivery days", example=5.2)
    tenure_days: int = Field(365, description="Days since signup", example=420)

class ReturnPredictionRequest(BaseModel):
    category: str = Field(..., example="Electronics")
    unit_price: float = Field(..., example=14500.0)
    discount_amount: float = Field(0.0, example=1200.0)
    delivery_days: int = Field(3, example=6)
    customer_return_history: float = Field(0.05, example=0.22)

class DemandPredictionRequest(BaseModel):
    horizon_days: int = Field(30, ge=1, le=90, description="Days ahead to forecast")

# Agent & Chat Request
class AgentInquiryRequest(BaseModel):
    question: str = Field(..., min_length=2, example="Why did profit decrease last month, which customers are at risk, and what should we do?")

class SafeSQLRequest(BaseModel):
    query: str = Field(..., example="Show top 10 products by profit in South")

class RAGQueryRequest(BaseModel):
    question: str = Field(..., example="What is our return policy for electronics?")
    top_k: int = Field(3, ge=1, le=10)

# Generic Response Wrapper
class StandardResponse(BaseModel):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None
