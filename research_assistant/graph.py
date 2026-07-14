"""LangGraph assembly and public workflow API."""

from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import END, START, StateGraph

from research_assistant.agents import ResearchAgents, create_llm
from research_assistant.config import Settings
from research_assistant.models import ResearchState
from research_assistant.search import DuckDuckGoSearch, SearchProvider


def route_after_review(state: ResearchState) -> Literal["researcher", "writer", "__end__"]:
    if state["review_decision"] == "approve":
        return END
    if state["review_decision"] == "research":
        return "researcher" if state["research_rounds"] < state["max_research_rounds"] else END
    return "writer" if state["draft_count"] < state["max_drafts"] else END


def build_graph(
    settings: Settings | None = None,
    *,
    llm: Any | None = None,
    search: SearchProvider | None = None,
):
    """Build the workflow; injected dependencies keep tests offline and deterministic."""
    if llm is None:
        llm = create_llm(settings or Settings.from_env())
    agents = ResearchAgents(llm=llm, search=search or DuckDuckGoSearch())

    workflow = StateGraph(ResearchState)
    workflow.add_node("researcher", agents.researcher)
    workflow.add_node("writer", agents.writer)
    workflow.add_node("reviewer", agents.reviewer)
    workflow.add_edge(START, "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "reviewer")
    workflow.add_conditional_edges(
        "reviewer",
        route_after_review,
        {"researcher": "researcher", "writer": "writer", END: END},
    )
    return workflow.compile()


def create_initial_state(
    topic: str,
    *,
    audience: str = "general reader",
    depth: str = "standard (about 700 words)",
    max_sources: int = 6,
    max_drafts: int = 3,
    max_research_rounds: int = 2,
) -> ResearchState:
    cleaned_topic = " ".join(topic.split())
    if len(cleaned_topic) < 3:
        raise ValueError("Please enter a research topic with at least 3 characters.")
    return {
        "topic": cleaned_topic[:500],
        "audience": audience,
        "depth": depth,
        "max_sources": max(3, min(max_sources, 10)),
        "sources": [],
        "research_notes": "",
        "report": "",
        "feedback": "",
        "review_decision": "rewrite",
        "draft_count": 0,
        "research_rounds": 0,
        "max_drafts": max(1, min(max_drafts, 5)),
        "max_research_rounds": max(1, min(max_research_rounds, 3)),
        "status": "ready",
    }
