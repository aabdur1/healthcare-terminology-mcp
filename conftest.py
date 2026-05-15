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


def pytest_addoption(parser):
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="run live tests that hit real NLM/CMS APIs",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-live"):
        return
    skip_live = pytest.mark.skip(reason="needs --run-live to execute")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
