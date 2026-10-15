"""
RAG Knowledge System & Agent Workflow Tests
Enterprise AI Business Decision Intelligence Platform
"""
import pytest
from rag.retriever import PolicyRAGRetriever
from rag.vector_store import policy_vector_store
from agents.orchestrator import business_decision_agent

def test_rag_vector_search():
    res = policy_vector_store.search("electronics return policy 14 days", top_k=2)
    assert len(res) > 0
    assert "01_return_and_refund_policy.md" in [r["document"] for r in res]
    assert res[0]["relevance_score"] > 0

def test_rag_retriever_grounding():
    retriever = PolicyRAGRetriever()
    ans = retriever.query_policy("What is the return window for electronics?")
    assert ans["is_grounded"] is True
    assert "14" in ans["answer"]
    assert len(ans["citations"]) > 0

def test_agent_orchestrator_planning():
    plan = business_decision_agent.plan_workflow("Why did profit decrease last month?")
    assert "root_cause_agent" in plan
    assert "insight_agent" in plan

def test_agent_full_inquiry_execution():
    res = business_decision_agent.execute_inquiry("Why did profit decrease last month, which customers are at risk, and what should we do?")
    assert "executive_summary" in res
    assert "evidence" in res
    assert "recommendations" in res
    assert "root_cause_analysis" in res
    assert len(res["recommendations"]) > 0
