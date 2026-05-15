# batch.py
from typing import Annotated, Any

from pydantic import Field

from server import mcp
import icd10
import loinc
import rxnorm


@mcp.tool(
    name="batch_search_icd10",
    description=(
        "Resolve a list of free-text clinical terms to ICD-10-CM codes in one "
        "call. Useful for coding a chart note in a single tool invocation. "
        "Returns a dict mapping each query to its matching codes."
    ),
)
def batch_search_icd10(
    queries: Annotated[
        list[str], Field(description="List of clinical terms to look up.")
    ],
    max_results_each: Annotated[
        int, Field(ge=1, le=20, description="Max matches per query.")
    ] = 5,
) -> dict[str, list[dict[str, str]]]:
    if not queries:
        raise ValueError("at least one query is required")
    return {q: icd10.search_icd10(q, max_results=max_results_each) for q in queries}


@mcp.tool(
    name="batch_search_loinc",
    description=(
        "Resolve a list of lab/observation terms to LOINC codes in one call."
    ),
)
def batch_search_loinc(
    queries: Annotated[list[str], Field(description="List of lab terms.")],
    max_results_each: Annotated[int, Field(ge=1, le=20)] = 5,
) -> dict[str, list[dict[str, str]]]:
    if not queries:
        raise ValueError("at least one query is required")
    return {q: loinc.search_loinc(q, max_results=max_results_each) for q in queries}


@mcp.tool(
    name="batch_search_rxnorm",
    description="Resolve a list of medication names to RxCUIs in one call.",
)
def batch_search_rxnorm(
    drug_names: Annotated[list[str], Field(description="List of drug names.")],
    max_results_each: Annotated[int, Field(ge=1, le=20)] = 5,
) -> dict[str, list[dict[str, Any]]]:
    if not drug_names:
        raise ValueError("at least one drug_name is required")
    return {
        d: rxnorm.search_rxnorm(d, max_results=max_results_each) for d in drug_names
    }
