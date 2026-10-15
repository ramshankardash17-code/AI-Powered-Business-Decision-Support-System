"""
Enterprise Agent Tools Definition
Enterprise AI Business Decision Intelligence Platform
Standardized Tool Interfaces for SQL, ML, Forecasting, RAG, and Inventory Diagnostics
"""
import logging
from typing import Dict, Any, List
from analytics.kpi_engine import KPIEngine
from analytics.root_cause import RootCauseAnalysisEngine
from analytics.inventory_intelligence import InventoryIntelligenceEngine
from ml.churn import ChurnModelPipeline
from ml.clv import CustomerLifetimeValueEngine
from dl.lstm_forecasting import DemandForecastingPipeline
from rag.retriever import PolicyRAGRetriever
from nlp.review_analyzer import ReviewNLPAnalyzer
from agents.text_to_sql import SafeTextToSQLEngine

logger = logging.getLogger(__name__)

class AgentTools:
    def __init__(self):
        self.kpi_engine = KPIEngine()
        self.rca_engine = RootCauseAnalysisEngine()
        self.inv_engine = InventoryIntelligenceEngine()
        self.churn_pipeline = ChurnModelPipeline()
        self.clv_engine = CustomerLifetimeValueEngine()
        self.dl_forecast = DemandForecastingPipeline()
        self.rag_retriever = PolicyRAGRetriever()
        self.review_nlp = ReviewNLPAnalyzer()
        self.text_to_sql = SafeTextToSQLEngine()

    def tool_run_sql(self, natural_language_query: str) -> Dict[str, Any]:
        """SQL Agent Tool: Converts query to safe SQL, executes and returns chart data"""
        return self.text_to_sql.natural_language_to_sql(natural_language_query)

    def tool_root_cause(self) -> Dict[str, Any]:
        """Root Cause Agent Tool: Dissects profit and revenue variances across dimensions"""
        return self.rca_engine.analyze_profit_decline()

    def tool_high_risk_customers(self) -> Dict[str, Any]:
        """ML Agent Tool: Retrieves high-churn and high-CLV customers needing retention"""
        return self.clv_engine.train_and_predict()

    def tool_inventory_status(self) -> Dict[str, Any]:
        """Inventory Tool: Scans stockout risks and reorder requirements"""
        return self.inv_engine.get_stockout_summary()

    def tool_demand_forecast(self, horizon_days: int = 30) -> Dict[str, Any]:
        """Forecast Agent Tool: Generates LSTM sequence forecast with prediction intervals"""
        forecast = self.dl_forecast.generate_future_forecast(horizon_days=horizon_days)
        benchmarks = self.dl_forecast.train_and_evaluate(epochs=15, test_days=30)
        return {
            "forecast_horizon_days": horizon_days,
            "forecast_series": forecast,
            "model_benchmarks": benchmarks
        }

    def tool_company_policy_rag(self, query: str) -> Dict[str, Any]:
        """RAG Agent Tool: Searches company SOPs, return policies, and business guidelines"""
        return self.rag_retriever.query_policy(query)

    def tool_customer_sentiment(self) -> Dict[str, Any]:
        """NLP Review Tool: Analyzes complaint topics and sentiment breakdown"""
        return {
            "complaints": self.review_nlp.get_complaint_topic_summary(),
            "category_sentiment": self.review_nlp.get_sentiment_by_category()
        }

agent_tools = AgentTools()
