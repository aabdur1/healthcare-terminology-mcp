# conftest.py
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import http_client


@pytest.fixture
def fake_responses(monkeypatch):
    """Replace http_client.get_json with a lookup table keyed by URL."""
    responses: dict[str, object] = {}

    def fake_get(url, params):
        if url not in responses:
            raise AssertionError(f"unexpected URL: {url} (params={params})")
        value = responses[url]
        return value(params) if callable(value) else value

    monkeypatch.setattr(http_client, "get_json", fake_get)
    return responses
