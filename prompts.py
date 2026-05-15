# prompts.py
from typing import Annotated

from pydantic import Field

from server import mcp


@mcp.prompt(
    name="code_chart_note",
    description=(
        "Extract every diagnosis, medication, and lab from a chart note and "
        "code them to ICD-10-CM, RxNorm, and LOINC."
    ),
)
def code_chart_note(
    chart_note: Annotated[str, Field(description="Free-text clinical chart note.")],
) -> str:
    return (
        "You are a clinical data coder. Read the chart note below and produce a "
        "structured table with three sections: Diagnoses, Medications, Labs.\n\n"
        "For each item:\n"
        "- Diagnoses: call `search_icd10` and return the best ICD-10-CM code.\n"
        "- Medications: call `search_rxnorm` and return the RxCUI plus canonical "
        "name. If a dosage is mentioned, note it.\n"
        "- Labs: call `search_loinc` and return the best LOINC code.\n\n"
        "If a term is ambiguous, return the top two candidates and flag it. "
        "Output a markdown table grouped by section.\n\n"
        f"<chart_note>\n{chart_note}\n</chart_note>"
    )


@mcp.prompt(
    name="summarize_med_list",
    description=(
        "Given a list of RxCUI identifiers, produce a clinical summary grouped "
        "by drug class with associated NDCs."
    ),
)
def summarize_med_list(
    rxcuis: Annotated[list[str], Field(description="List of RxNorm RxCUI identifiers.")],
) -> str:
    rxcui_lines = "\n".join(f"- {r}" for r in rxcuis)
    return (
        "You are a clinical pharmacist. For each RxCUI below:\n"
        "1. Use the `search_rxnorm` data or your knowledge to identify the drug "
        "name and class.\n"
        "2. Call `rxcui_to_ndcs` to enumerate every packaged NDC for that drug.\n"
        "3. Group results by therapeutic class.\n\n"
        "Output a markdown report with sections per drug class, listing drug "
        "name, RxCUI, and bullet list of NDCs.\n\n"
        f"<rxcuis>\n{rxcui_lines}\n</rxcuis>"
    )
