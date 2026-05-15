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


@mcp.tool(
    name="ndc_to_rxcui",
    description=(
        "Map a National Drug Code (NDC) to its RxNorm RxCUI. NDC is the "
        "identifier on prescription packaging; RxCUI is the clinical concept "
        "used in EHRs. Returns the RxCUI or None if no match."
    ),
)
def ndc_to_rxcui(
    ndc: Annotated[str, Field(description="11-digit NDC, hyphenated or plain.")],
) -> dict[str, Any]:
    if not ndc.strip():
        raise ValueError("ndc cannot be empty")

    data = http_client.get_json(
        f"{RXNORM_BASE}/rxcui.json",
        {"idtype": "NDC", "id": ndc},
    )
    rxnorm_ids = data.get("idGroup", {}).get("rxnormId") or []
    return {"ndc": ndc, "rxcui": rxnorm_ids[0] if rxnorm_ids else None}


@mcp.tool(
    name="rxcui_to_ndcs",
    description=(
        "List every NDC associated with a given RxNorm RxCUI. Useful for "
        "expanding a clinical drug concept into all packaged forms found "
        "in pharmacy claims data."
    ),
)
def rxcui_to_ndcs(
    rxcui: Annotated[str, Field(description="RxNorm RxCUI identifier.")],
) -> dict[str, Any]:
    if not rxcui.strip():
        raise ValueError("rxcui cannot be empty")

    data = http_client.get_json(
        f"{RXNORM_BASE}/rxcui/{rxcui}/ndcs.json", {}
    )
    ndcs = data.get("ndcGroup", {}).get("ndcList", {}).get("ndc", []) or []
    return {"rxcui": rxcui, "ndcs": list(ndcs)}
