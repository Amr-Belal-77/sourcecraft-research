from types import SimpleNamespace

from langgraph.graph import END

from research_assistant.graph import build_graph, create_initial_state, route_after_review


class FakeSearch:
    def __init__(self):
        self.calls = 0

    def search(self, query: str, max_results: int):
        self.calls += 1
        return [
            {
                "title": f"Reliable source {self.calls}",
                "url": f"https://example.com/source-{self.calls}",
                "snippet": "A factual test snippet.",
            }
        ]


class FailingSearch:
    def search(self, query: str, max_results: int):
        raise TimeoutError("search provider timed out")


class FakeLLM:
    def __init__(self, replies: list[str]):
        self.replies = iter(replies)

    def invoke(self, _prompt: str):
        return SimpleNamespace(content=next(self.replies))


def test_create_initial_state_normalizes_and_bounds_input():
    state = create_initial_state("  edge   AI  ", max_sources=99, max_drafts=99)
    assert state["topic"] == "edge AI"
    assert state["max_sources"] == 10
    assert state["max_drafts"] == 5


def test_route_after_review_obeys_limits():
    state = create_initial_state("test topic")
    state.update(review_decision="approve")
    assert route_after_review(state) == END

    state.update(review_decision="rewrite", draft_count=1)
    assert route_after_review(state) == "writer"

    state.update(review_decision="research", research_rounds=2)
    assert route_after_review(state) == END


def test_full_graph_approves_a_report_offline():
    llm = FakeLLM(
        [
            "Evidence-backed notes [1].",
            "# Report\nA supported claim [1].\n\n## Sources\n1. [Source](https://example.com/source-1)",
            '{"decision":"approve","feedback":"Ready to publish."}',
        ]
    )
    graph = build_graph(llm=llm, search=FakeSearch())

    result = graph.invoke(create_initial_state("responsible edge AI"))

    assert result["status"] == "approved"
    assert result["draft_count"] == 1
    assert result["research_rounds"] == 1
    assert len(result["sources"]) == 1


def test_reviewer_can_request_more_research():
    search = FakeSearch()
    llm = FakeLLM(
        [
            "Initial notes [1].",
            "Initial report [1].",
            '{"decision":"research","feedback":"Find evidence about limitations."}',
            "Expanded notes [1] [2].",
            "Improved report [1] [2].",
            '{"decision":"approve","feedback":"Evidence is now sufficient."}',
        ]
    )
    graph = build_graph(llm=llm, search=search)

    result = graph.invoke(create_initial_state("small language models"))

    assert result["status"] == "approved"
    assert result["research_rounds"] == 2
    assert result["draft_count"] == 2
    assert search.calls == 2
    assert len(result["sources"]) == 2


def test_search_failure_degrades_to_a_reviewable_report():
    llm = FakeLLM(
        [
            "# Unverified report\nNo sources were available.",
            '{"decision":"approve","feedback":"The limitation is explicit."}',
            "# Still unverified\nThe retry also returned no sources.",
            '{"decision":"approve","feedback":"The limitation is explicit."}',
        ]
    )
    graph = build_graph(llm=llm, search=FailingSearch())

    result = graph.invoke(create_initial_state("a test topic"))

    assert result["research_notes"].startswith("No web sources")
    assert result["sources"] == []
    assert result["research_rounds"] == 2
    assert result["status"] == "max_iterations_reached"
