"""Small, provider-tolerant text parsing helpers."""

from __future__ import annotations

import json
import re
from typing import Any


def response_text(response: Any) -> str:
    """Extract text from LangChain responses with string or block content."""
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return str(content)

    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
    return "".join(parts)


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object even when the model wraps it in a Markdown fence."""
    cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip(), flags=re.I)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("The reviewer did not return a JSON object.")
    value = json.loads(cleaned[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("The reviewer response must be a JSON object.")
    return value
