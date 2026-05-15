# main.py
from server import mcp

import icd10  # noqa: F401
import loinc  # noqa: F401
import rxnorm  # noqa: F401
import npi  # noqa: F401


@mcp.resource("terminology://about")
def about() -> str:
    # Update this string when tools are added (tracked in Task 12).
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
