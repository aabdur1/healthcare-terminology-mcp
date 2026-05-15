from typing import Annotated, Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("Healthcare Terminology")

ICD10_URL = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
LOINC_URL = "https://clinicaltables.nlm.nih.gov/api/loinc_items/v3/search"
RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"

HTTP_TIMEOUT = 10.0


def _get_json(url: str, params: dict[str, Any]) -> Any:
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool(
    name="search_icd10",
    description=(
        "Search ICD-10-CM diagnosis codes by free-text term (e.g. 'type 2 diabetes', "
        "'pneumonia', 'fracture left wrist'). Returns a list of matching codes with "
        "their official descriptions. Use this when the user asks for a diagnosis code, "
        "wants to map a clinical phrase to ICD-10, or is exploring related conditions."
    ),
)
def search_icd10(
    query: Annotated[str, Field(description="Free-text clinical term to look up.")],
    max_results: Annotated[
        int,
        Field(ge=1, le=50, description="Maximum number of matching codes to return."),
    ] = 10,
) -> list[dict[str, str]]:
    if not query.strip():
        raise ValueError("query cannot be empty")

    data = _get_json(
        ICD10_URL,
        {
            "terms": query,
            "count": max_results,
            "sf": "code,name",
            "df": "code,name",
        },
    )

    rows = data[3] if len(data) > 3 and data[3] else []
    return [{"code": row[0], "description": row[1]} for row in rows]


@mcp.tool(
    name="search_loinc",
    description=(
        "Search LOINC lab/observation codes by free-text term (e.g. 'hemoglobin a1c', "
        "'serum potassium', 'blood pressure systolic'). Returns LOINC numbers with their "
        "long common names. Use this for mapping lab orders or vital signs to LOINC."
    ),
)
def search_loinc(
    query: Annotated[
        str, Field(description="Free-text lab or observation term to look up.")
    ],
    max_results: Annotated[
        int,
        Field(ge=1, le=50, description="Maximum number of matching codes to return."),
    ] = 10,
) -> list[dict[str, str]]:
    if not query.strip():
        raise ValueError("query cannot be empty")

    data = _get_json(
        LOINC_URL,
        {
            "terms": query,
            "maxList": max_results,
            "df": "LOINC_NUM,LONG_COMMON_NAME,COMPONENT,SYSTEM",
        },
    )

    rows = data[3] if len(data) > 3 and data[3] else []
    return [
        {
            "code": row[0],
            "long_common_name": row[1],
            "component": row[2] if len(row) > 2 else "",
            "system": row[3] if len(row) > 3 else "",
        }
        for row in rows
    ]


@mcp.tool(
    name="search_rxnorm",
    description=(
        "Search RxNorm for medication concepts by name (brand or generic). Uses RxNav's "
        "approximate-match endpoint so partial spellings and brand names both work "
        "(e.g. 'metformin', 'Lipitor', 'amox 500'). Returns RxCUI identifiers with "
        "their canonical RxNorm names and match scores."
    ),
)
def search_rxnorm(
    drug_name: Annotated[str, Field(description="Medication name (brand or generic).")],
    max_results: Annotated[
        int,
        Field(
            ge=1, le=50, description="Maximum number of matching concepts to return."
        ),
    ] = 10,
) -> list[dict[str, Any]]:
    if not drug_name.strip():
        raise ValueError("drug_name cannot be empty")

    data = _get_json(
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
        data = _get_json(f"{RXNORM_BASE}/rxcui/{rxcui}/properties.json", {})
        return data.get("properties", {}).get("name", "")
    except httpx.HTTPError:
        return ""


@mcp.resource("terminology://about")
def about() -> str:
    return (
        "Healthcare Terminology MCP\n\n"
        "Tools:\n"
        "  - search_icd10: ICD-10-CM diagnosis codes (NLM Clinical Tables)\n"
        "  - search_loinc: LOINC lab/observation codes (NLM Clinical Tables)\n"
        "  - search_rxnorm: RxNorm medication concepts (NLM RxNav)\n\n"
        "All endpoints are public and require no API key."
    )


if __name__ == "__main__":
    mcp.run()
