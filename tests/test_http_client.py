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

        def get(self, url, params):
            captured["url"] = url
            captured["params"] = params
            return FakeResponse()

    monkeypatch.setattr(http_client.httpx, "Client", FakeClient)

    result = http_client.get_json("https://example.com", {"q": "x"})

    assert result == {"ok": True}
    assert captured == {"url": "https://example.com", "params": {"q": "x"}}
