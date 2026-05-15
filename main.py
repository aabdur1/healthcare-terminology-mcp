# main.py
from server import mcp

import hcpcs  # noqa: F401
import icd10  # noqa: F401
import loinc  # noqa: F401
import rxnorm  # noqa: F401
import npi  # noqa: F401
import batch  # noqa: F401
import prompts  # noqa: F401


@mcp.resource("terminology://about")
def about() -> str:
    return (
        "Healthcare Terminology MCP\n\n"
        "Terminology search:\n"
        "  - search_icd10 / expand_icd10: ICD-10-CM diagnosis codes\n"
        "  - search_loinc: LOINC lab/observation codes\n"
        "  - search_rxnorm: RxNorm medication concepts\n"
        "  - search_hcpcs: HCPCS Level II Medicare codes\n"
        "  - search_npi: CMS provider directory\n\n"
        "Crosswalks:\n"
        "  - ndc_to_rxcui, rxcui_to_ndcs\n\n"
        "Batch operations:\n"
        "  - batch_search_icd10, batch_search_loinc, batch_search_rxnorm\n\n"
        "Prompts:\n"
        "  - code_chart_note, summarize_med_list\n\n"
        "All endpoints are public and require no API key."
    )


if __name__ == "__main__":
    mcp.run()
