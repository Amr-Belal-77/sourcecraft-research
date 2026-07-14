"""Shared state and source models for the LangGraph workflow."""

from __future__ import annotations

from typing import Literal, TypedDict


class Source(TypedDict):
    title: str
    url: str
    snippet: str


ReviewDecision = Literal["approve", "rewrite", "research"]


class ResearchState(TypedDict):
    topic: str
    audience: str
    depth: str
    max_sources: int
    sources: list[Source]
    research_notes: str
    report: str
    feedback: str
    review_decision: ReviewDecision
    draft_count: int
    research_rounds: int
    max_drafts: int
    max_research_rounds: int
    status: str
