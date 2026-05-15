import httpx
import pytest

import http_client


def test_get_json_round_trip(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": True}

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def get(self, url, *, params=None):
            captured["url"] = url
            captured["params"] = params
            return FakeResponse()

    monkeypatch.setattr(http_client.httpx, "Client", FakeClient)

    result = http_client.get_json("https://example.com", {"q": "x"})

    assert result == {"ok": True}
    assert captured == {"url": "https://example.com", "params": {"q": "x"}}


def test_get_json_propagates_http_error(monkeypatch):
    class ErrorResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "404 Not Found",
                request=httpx.Request("GET", "https://example.com"),
                response=httpx.Response(404),
            )

        def json(self):
            return {}

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def get(self, url, *, params=None):
            return ErrorResponse()

    monkeypatch.setattr(http_client.httpx, "Client", FakeClient)

    with pytest.raises(httpx.HTTPStatusError):
        http_client.get_json("https://example.com", {"q": "x"})
