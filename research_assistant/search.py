"""Search adapters. Replace this module to use Tavily, arXiv, or an internal index."""

from __future__ import annotations

from typing import Protocol
from urllib.parse import urlparse

from ddgs import DDGS

from research_assistant.models import Source


class SearchProvider(Protocol):
    def search(self, query: str, max_results: int) -> list[Source]: ...


class DuckDuckGoSearch:
    """Free search provider that does not require another API key."""

    def search(self, query: str, max_results: int) -> list[Source]:
        raw_results = DDGS().text(query, max_results=max_results)
        sources: list[Source] = []
        seen: set[str] = set()

        for item in raw_results:
            url = str(item.get("href") or item.get("url") or "").strip()
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or url in seen:
                continue
            seen.add(url)
            sources.append(
                {
                    "title": str(item.get("title") or parsed.netloc).strip(),
                    "url": url,
                    "snippet": str(item.get("body") or item.get("snippet") or "").strip(),
                }
            )
        return sources


def merge_sources(existing: list[Source], new: list[Source]) -> list[Source]:
    """Combine search rounds without duplicating URLs."""
    merged: dict[str, Source] = {source["url"]: source for source in existing}
    for source in new:
        merged.setdefault(source["url"], source)
    return list(merged.values())
