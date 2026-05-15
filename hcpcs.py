# hcpcs.py
from typing import Annotated

from pydantic import Field

from server import mcp
import http_client

HCPCS_URL = "https://clinicaltables.nlm.nih.gov/api/hcpcs/v3/search"


@mcp.tool(
    name="search_hcpcs",
    description=(
        "Search HCPCS Level II codes (Medicare procedure/DME/drug-administration "
        "codes; distinct from CPT). Returns matching codes with short "
        "descriptors. Use for Medicare claims analysis."
    ),
)
def search_hcpcs(
    query: Annotated[str, Field(description="Free-text HCPCS term.")],
    max_results: Annotated[
        int, Field(ge=1, le=50, description="Max matching codes to return.")
    ] = 10,
) -> list[dict[str, str]]:
    if not query.strip():
        raise ValueError("query cannot be empty")

    data = http_client.get_json(
        HCPCS_URL,
        {
            "terms": query,
            "count": max_results,
            "sf": "code,short_desc",
            "df": "code,short_desc",
        },
    )
    rows = data[3] if len(data) > 3 and data[3] else []
    return [{"code": row[0], "description": row[1]} for row in rows]
