"""
Agentic AI & Business Decision Intelligence API Router
Enterprise AI Business Decision Intelligence Platform
Coordinates Planner, SQL, ML, Forecast, RAG, and Insight Agents
"""
from fastapi import APIRouter, HTTPException
from agents.orchestrator import business_decision_agent
from agents.text_to_sql import SafeTextToSQLEngine
from analytics.root_cause import RootCauseAnalysisEngine
from rag.retriever import PolicyRAGRetriever
from api.schemas import AgentInquiryRequest, SafeSQLRequest, RAGQueryRequest, StandardResponse

router = APIRouter(prefix="/api/agent", tags=["AI Business Analyst & Agents"])
sql_engine = SafeTextToSQLEngine()
rca_engine = RootCauseAnalysisEngine()
rag_retriever = PolicyRAGRetriever()

@router.post("/inquire", response_model=StandardResponse)
def execute_agent_inquiry(req: AgentInquiryRequest):
    """
    Primary AI Business Analyst conversational endpoint.
    Orchestrates Planner, SQL, ML, Forecast, RAG, and Insight agents to deliver
    factually verified, evidence-backed business insights with zero numerical hallucination.
    """
    try:
        result = business_decision_agent.execute_inquiry(req.question)
        return StandardResponse(success=True, data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sql", response_model=StandardResponse)
def generate_and_execute_safe_sql(req: SafeSQLRequest):
    """
    Safe Text-to-SQL endpoint. Validates read-only permissions, blocks DDL/DML,
    executes query against Star Schema and returns chart-ready series with explanation.
    """
    result = sql_engine.natural_language_to_sql(req.query)
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "SQL validation failed."))
    return StandardResponse(success=True, data=result)

@router.post("/root-cause", response_model=StandardResponse)
def execute_root_cause_analysis():
    """Executes multi-dimensional variance decomposition across category, product, region, and inventory"""
    data = rca_engine.analyze_profit_decline()
    return StandardResponse(success=True, data=data)

@router.post("/rag", response_model=StandardResponse)
def query_company_policies(req: RAGQueryRequest):
    """Retrieves verified corporate policies, refund SOPs, and inventory rules with exact citations"""
    data = rag_retriever.query_policy(req.question, top_k=req.top_k)
    return StandardResponse(success=True, data=data)
