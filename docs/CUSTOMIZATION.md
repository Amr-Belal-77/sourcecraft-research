# Customization guide

SourceCraft is intentionally split into small modules so a new research domain does not require
rewriting the graph.

## Fastest path to a new domain

1. Rename the product and adjust the Streamlit copy in `streamlit_app.py`.
2. Edit the three role prompts in `research_assistant/prompts.py`.
3. Replace `DuckDuckGoSearch` in `research_assistant/search.py` if the domain needs a specialist
   source such as arXiv, PubMed, company documents, or a vector database.
4. Add inputs to `ResearchState` and `create_initial_state` when the domain needs filters such as
   date range, country, industry, or academic level.
5. Add a test that covers the new reviewer decision before changing graph routing.

## Agent responsibilities

| Agent | Owns | Should not own |
|---|---|---|
| Researcher | Search queries, source collection, evidence notes | Final prose |
| Writer | Structure, audience, synthesis, inline citations | Inventing new evidence |
| Reviewer | Quality gate and routing decision | Silently rewriting the report |

Keeping these boundaries makes failures observable. A missing fact goes back to the Researcher;
unclear writing goes back to the Writer.

## Recommended domain adaptations

### AI paper scout

- Search: arXiv and Hugging Face papers.
- Output: problem, method, datasets, metrics, limitations, and code links.
- Review rule: reject metric comparisons that use different datasets or evaluation settings.

### Market intelligence brief

- Search: company investor relations pages, regulator filings, and reputable industry sources.
- Output: market map, competitor table, signals, risks, and dated evidence.
- Review rule: distinguish reported facts from estimates and opinions.

### Policy comparison assistant

- Search: official government and regulator domains.
- Output: jurisdiction-by-jurisdiction comparison with effective dates.
- Review rule: flag stale sources and avoid legal advice.

## Adding a search provider

Implement the small `SearchProvider` protocol:

```python
class MySearch:
    def search(self, query: str, max_results: int) -> list[Source]:
        return [{"title": "...", "url": "https://...", "snippet": "..."}]
```

Then inject it with `build_graph(search=MySearch())`. Keep credentials in environment variables or
deployment secrets, never in code or notebook cells.

## Production upgrades

- Add a trusted-domain allowlist for high-stakes research.
- Fetch and parse the full pages; search snippets alone are not enough for rigorous research.
- Store runs and feedback in a database.
- Add rate limiting, authentication, request timeouts, and observability.
- Add citation entailment checks that compare each claim with the underlying page text.
- Add human approval before publishing or using results in decisions.
