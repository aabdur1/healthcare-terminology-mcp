# loinc.py
from typing import Annotated

from pydantic import Field

from server import mcp
import http_client

LOINC_URL = "https://clinicaltables.nlm.nih.gov/api/loinc_items/v3/search"


@mcp.tool(
    name="search_loinc",
    description=(
        "Search LOINC lab/observation codes by free-text term. Returns LOINC "
        "numbers with long common names, component, and system."
    ),
)
def search_loinc(
    query: Annotated[str, Field(description="Free-text lab term.")],
    max_results: Annotated[
        int, Field(ge=1, le=50, description="Max matching codes to return.")
    ] = 10,
) -> list[dict[str, str]]:
    if not query.strip():
        raise ValueError("query cannot be empty")

    data = http_client.get_json(
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
