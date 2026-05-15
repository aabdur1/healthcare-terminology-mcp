# Healthcare Terminology MCP

[![tests](https://github.com/aabdur1/healthcare-terminology-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/aabdur1/healthcare-terminology-mcp/actions/workflows/test.yml)

An [MCP](https://modelcontextprotocol.io) server that lets Claude (or any MCP client) look up clinical codes from the U.S. National Library of Medicine's public APIs:

- **ICD-10-CM** diagnosis codes
- **LOINC** lab and observation codes
- **RxNorm** medication concepts

No API keys required.

## Tools

### Terminology search
| Tool | Description |
|---|---|
| `search_icd10(query, max_results)` | ICD-10-CM diagnosis codes. |
| `expand_icd10(prefix, max_results)` | All subcodes under an ICD-10-CM category prefix. |
| `search_loinc(query, max_results)` | LOINC lab and observation codes. |
| `search_rxnorm(drug_name, max_results)` | RxNorm medication concepts. |
| `search_hcpcs(query, max_results)` | HCPCS Level II Medicare codes. |
| `search_npi(...)` | CMS NPI Registry provider lookup. |

### Crosswalks
| Tool | Description |
|---|---|
| `ndc_to_rxcui(ndc)` | National Drug Code → RxNorm RxCUI. |
| `rxcui_to_ndcs(rxcui)` | RxNorm RxCUI → all packaged NDCs. |

### Batch operations
| Tool | Description |
|---|---|
| `batch_search_icd10(queries, max_results_each)` | Resolve a list of terms to ICD-10. |
| `batch_search_loinc(queries, max_results_each)` | Resolve a list of terms to LOINC. |
| `batch_search_rxnorm(drug_names, max_results_each)` | Resolve a list of drug names to RxNorm. |

## Prompts

| Prompt | Description |
|---|---|
| `code_chart_note(chart_note)` | Extract diagnoses, meds, and labs from a note and code them all. |
| `summarize_med_list(rxcuis)` | Group a medication list by class and enumerate NDCs. |

## Resources

| URI | Description |
|---|---|
| `terminology://about` | Plain-text overview of the server. |

## Setup

Requires Python 3.10+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/aabdur1/healthcare-terminology-mcp.git
cd healthcare-terminology-mcp
uv sync
```

## Run

Local stdio server (the form an MCP client uses):

```bash
uv run main.py
```

Interactive browser inspector for testing tools manually:

```bash
uv run mcp dev main.py
```

## Use with Claude Code

```bash
claude mcp add healthcare-terminology -- uv --directory /absolute/path/to/healthcare-terminology-mcp run main.py
```

Then in any Claude Code session:

> Look up the ICD-10 code for chronic kidney disease stage 3.

## Usage examples

### Coding a chart note
```
> Use the code_chart_note prompt with this note:
> "65 y/o male with type 2 DM on metformin, A1c 8.2%, BP 158/92"
```

### Bridging pharmacy and clinical data
```
> I have an NDC 00378-0518-77 from a claim. What's the RxCUI and what other
> packaged forms exist for that drug?
```
Claude will call `ndc_to_rxcui` then `rxcui_to_ndcs`.

### Provider lookup
```
> Find internal medicine doctors named Smith in Illinois.
```

### Rollup query
```
> Give me every ICD-10 code under E11 (type 2 diabetes).
```

## Data sources

- [NLM Clinical Tables Search Service](https://clinicaltables.nlm.nih.gov/) — ICD-10-CM, LOINC, HCPCS
- [NLM RxNav](https://rxnav.nlm.nih.gov/) — RxNorm, NDC crosswalks
- [CMS NPI Registry](https://npiregistry.cms.hhs.gov/) — Provider lookup

All endpoints are public and require no API key.
