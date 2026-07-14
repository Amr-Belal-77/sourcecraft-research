from types import SimpleNamespace

import pytest

from research_assistant.text import parse_json_object, response_text


def test_response_text_supports_block_content():
    response = SimpleNamespace(
        content=[
            {"type": "thinking", "thinking": "hidden"},
            {"type": "text", "text": "Hello"},
            " world",
        ]
    )
    assert response_text(response) == "Hello world"


def test_parse_json_object_accepts_markdown_fence():
    result = parse_json_object('```json\n{"decision":"approve","feedback":"Ready"}\n```')
    assert result == {"decision": "approve", "feedback": "Ready"}


def test_parse_json_object_rejects_plain_text():
    with pytest.raises(ValueError):
        parse_json_object("APPROVED")
