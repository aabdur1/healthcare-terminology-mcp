# icd10.py
from typing import Annotated

from pydantic import Field

from server import mcp
import http_client

ICD10_URL = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"


@mcp.tool(
    name="search_icd10",
    description=(
        "Search ICD-10-CM diagnosis codes by free-text term. Returns matching "
        "codes with descriptions. Use for mapping clinical phrases to ICD-10."
    ),
)
def search_icd10(
    query: Annotated[str, Field(description="Free-text clinical term.")],
    max_results: Annotated[
        int, Field(ge=1, le=50, description="Max matching codes to return.")
    ] = 10,
) -> list[dict[str, str]]:
    if not query.strip():
        raise ValueError("query cannot be empty")

    data = http_client.get_json(
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
