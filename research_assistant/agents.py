"""The Researcher, Writer, and Reviewer graph nodes."""

from __future__ import annotations

from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from research_assistant.config import Settings
from research_assistant.models import ResearchState
from research_assistant.prompts import research_prompt, reviewer_prompt, writer_prompt
from research_assistant.search import SearchProvider, merge_sources
from research_assistant.text import parse_json_object, response_text


def create_llm(settings: Settings) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.model,
        google_api_key=settings.require_api_key(),
        temperature=settings.temperature,
        max_output_tokens=8192,
    )


class ResearchAgents:
    """Dependency-injected graph nodes that are simple to test and replace."""

    def __init__(self, llm: Any, search: SearchProvider) -> None:
        self.llm = llm
        self.search = search

    def researcher(self, state: ResearchState) -> dict[str, Any]:
        query = state["topic"]
        if state["feedback"]:
            query = f"{query} {state['feedback']}"

        try:
            new_sources = self.search.search(query, state["max_sources"])
        except Exception:  # Search is external; preserve a useful partial run if unavailable.
            new_sources = []
        sources = merge_sources(state["sources"], new_sources)
        if not sources:
            return {
                "research_notes": "No web sources were returned. The report cannot be verified.",
                "research_rounds": state["research_rounds"] + 1,
                "status": "no_sources",
            }

        notes = response_text(self.llm.invoke(research_prompt(state, sources)))
        return {
            "sources": sources,
            "research_notes": notes,
            "research_rounds": state["research_rounds"] + 1,
            "status": "research_complete",
        }

    def writer(self, state: ResearchState) -> dict[str, Any]:
        report = response_text(self.llm.invoke(writer_prompt(state)))
        return {
            "report": report,
            "draft_count": state["draft_count"] + 1,
            "status": "draft_complete",
        }

    def reviewer(self, state: ResearchState) -> dict[str, Any]:
        raw_review = response_text(self.llm.invoke(reviewer_prompt(state)))
        try:
            review = parse_json_object(raw_review)
            decision = str(review.get("decision", "rewrite")).lower()
            if decision not in {"approve", "rewrite", "research"}:
                decision = "rewrite"
            feedback = str(review.get("feedback", "Improve and verify the draft."))
        except (ValueError, TypeError):
            decision = "rewrite"
            feedback = "Reviewer output was malformed; rewrite the report conservatively."

        if not state["sources"]:
            decision = "research"
            feedback = "No verifiable web sources are available; do not publish this report."

        status = "approved" if decision == "approve" else f"needs_{decision}"
        if decision == "rewrite" and state["draft_count"] >= state["max_drafts"]:
            status = "max_iterations_reached"
        if decision == "research" and state["research_rounds"] >= state["max_research_rounds"]:
            status = "max_iterations_reached"

        return {
            "review_decision": decision,
            "feedback": feedback,
            "status": status,
        }
