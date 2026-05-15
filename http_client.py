from typing import Any

import httpx

HTTP_TIMEOUT = 10.0


def get_json(url: str, params: dict[str, Any]) -> Any:
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()
