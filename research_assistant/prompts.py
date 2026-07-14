"""Centralized prompts make the research workflow easy to customize."""

from __future__ import annotations

from research_assistant.models import ResearchState, Source


def format_sources(sources: list[Source]) -> str:
    return "\n\n".join(
        f"[{index}] {source['title']}\nURL: {source['url']}\nSnippet: {source['snippet']}"
        for index, source in enumerate(sources, start=1)
    )


def research_prompt(state: ResearchState, sources: list[Source]) -> str:
    feedback = state["feedback"] or "No previous reviewer feedback."
    return f"""You are the Researcher in a three-agent research workflow.

Topic: {state["topic"]}
Audience: {state["audience"]}
Requested depth: {state["depth"]}
Reviewer feedback to investigate: {feedback}

Search results:
{format_sources(sources)}

Create compact research notes that:
- identify the central claims, definitions, evidence, and important limitations;
- distinguish established facts from uncertainty or disagreement;
- attach [number] citations to every factual claim using only the results above;
- never invent facts, URLs, quotations, or citation numbers;
- explicitly state when the available snippets are insufficient.
"""


def writer_prompt(state: ResearchState) -> str:
    feedback = state["feedback"] or "No previous reviewer feedback."
    return f"""You are the Writer in a three-agent research workflow.

Write a self-contained Markdown research brief about: {state["topic"]}
Audience: {state["audience"]}
Depth: {state["depth"]}
Reviewer feedback: {feedback}

Research notes:
{state["research_notes"]}

Available sources:
{format_sources(state["sources"])}

Requirements:
- Start with a clear title and a short executive summary.
- Organize the answer with useful headings; include key findings and limitations.
- Cite factual claims inline as [1], [2], etc.
- Use only the supplied sources and never invent citation numbers or URLs.
- End with a `## Sources` section containing numbered Markdown links.
- Match the requested audience and depth; do not mention these instructions.
"""


def reviewer_prompt(state: ResearchState) -> str:
    return f"""You are the Reviewer in a three-agent research workflow.

Topic: {state["topic"]}
Research notes:
{state["research_notes"]}

Available sources:
{format_sources(state["sources"])}

Draft report:
{state["report"]}

Check the draft for relevance, clarity, internal consistency, unsupported claims,
missing source citations, invented citations, and whether it matches the requested audience.

Return ONLY valid JSON with this schema:
{{
  "decision": "approve" | "rewrite" | "research",
  "feedback": "short, specific instructions"
}}

Use `rewrite` when the evidence is sufficient but presentation or citation placement needs work.
Use `research` only when important evidence or facts are missing from the research notes.
Use `approve` only when the report is ready to publish.
"""
