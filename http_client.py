# http_client.py
from functools import lru_cache
from typing import Any

import httpx

HTTP_TIMEOUT = 10.0
CACHE_SIZE = 512


def get_json(url: str, params: dict[str, Any]) -> Any:
    """Cached GET-as-JSON. Params dict is normalized to a hashable tuple."""
    key = tuple(sorted(params.items())) if params else ()
    return _cached_get(url, key)


@lru_cache(maxsize=CACHE_SIZE)
def _cached_get(url: str, key: tuple) -> Any:
    params = dict(key)
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def clear_cache() -> None:
    _cached_get.cache_clear()
