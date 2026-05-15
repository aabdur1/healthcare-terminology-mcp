# rxnorm.py
from typing import Annotated, Any

import httpx
from pydantic import Field

from server import mcp
import http_client

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"


@mcp.tool(
    name="search_rxnorm",
    description=(
        "Search RxNorm for medications by name (brand or generic). Uses "
        "RxNav approximate-match so partial spellings work. Returns RxCUI "
        "identifiers with canonical names and match scores."
    ),
)
def search_rxnorm(
    drug_name: Annotated[str, Field(description="Medication name.")],
    max_results: Annotated[
        int, Field(ge=1, le=50, description="Max matching concepts to return.")
    ] = 10,
) -> list[dict[str, Any]]:
    if not drug_name.strip():
        raise ValueError("drug_name cannot be empty")

    data = http_client.get_json(
        f"{RXNORM_BASE}/approximateTerm.json",
        {"term": drug_name, "maxEntries": max_results},
    )

    candidates = data.get("approximateGroup", {}).get("candidate", []) or []
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for c in candidates:
        rxcui = c.get("rxcui")
        if not rxcui or rxcui in seen:
            continue
        seen.add(rxcui)
        results.append(
            {
                "rxcui": rxcui,
                "name": _rxnorm_name(rxcui),
                "score": float(c.get("score", 0)),
            }
        )
        if len(results) >= max_results:
            break
    return results


def _rxnorm_name(rxcui: str) -> str:
    try:
        data = http_client.get_json(
            f"{RXNORM_BASE}/rxcui/{rxcui}/properties.json", {}
        )
        return data.get("properties", {}).get("name", "")
    except httpx.HTTPError:
        return ""
