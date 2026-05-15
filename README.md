# Healthcare Terminology MCP

An [MCP](https://modelcontextprotocol.io) server that lets Claude (or any MCP client) look up clinical codes from the U.S. National Library of Medicine's public APIs:

- **ICD-10-CM** diagnosis codes
- **LOINC** lab and observation codes
- **RxNorm** medication concepts

No API keys required.

## Tools

| Tool | Description |
|---|---|
| `search_icd10(query, max_results)` | Search ICD-10-CM diagnosis codes by free-text term. |
| `search_loinc(query, max_results)` | Search LOINC lab/observation codes by free-text term. |
| `search_rxnorm(drug_name, max_results)` | Approximate-match search for RxNorm medication concepts. |

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

## Data sources

- [NLM Clinical Tables Search Service](https://clinicaltables.nlm.nih.gov/) — ICD-10-CM, LOINC
- [NLM RxNav](https://rxnav.nlm.nih.gov/) — RxNorm
