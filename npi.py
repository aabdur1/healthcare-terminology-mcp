# npi.py
from typing import Annotated, Any, Optional

from pydantic import Field

from server import mcp
import http_client

NPI_URL = "https://npiregistry.cms.hhs.gov/api/"


@mcp.tool(
    name="search_npi",
    description=(
        "Search the CMS National Provider Identifier (NPI) Registry. Look up "
        "providers by NPI number, name, organization, taxonomy, city, or state. "
        "Returns provider name, primary specialty (taxonomy), and practice "
        "address. At least one filter argument is required."
    ),
)
def search_npi(
    npi_number: Annotated[
        Optional[str], Field(default=None, description="10-digit NPI.")
    ] = None,
    first_name: Annotated[
        Optional[str], Field(default=None, description="Provider first name.")
    ] = None,
    last_name: Annotated[
        Optional[str], Field(default=None, description="Provider last name.")
    ] = None,
    organization_name: Annotated[
        Optional[str], Field(default=None, description="Organization name.")
    ] = None,
    taxonomy_description: Annotated[
        Optional[str], Field(default=None, description="Specialty / taxonomy.")
    ] = None,
    city: Annotated[Optional[str], Field(default=None, description="City.")] = None,
    state: Annotated[
        Optional[str], Field(default=None, description="2-letter state code.")
    ] = None,
    max_results: Annotated[
        int, Field(ge=1, le=200, description="Max providers to return.")
    ] = 10,
) -> list[dict[str, Any]]:
    filters = {
        "number": npi_number,
        "first_name": first_name,
        "last_name": last_name,
        "organization_name": organization_name,
        "taxonomy_description": taxonomy_description,
        "city": city,
        "state": state,
    }
    active = {k: v for k, v in filters.items() if v}
    if not active:
        raise ValueError("at least one search filter is required")

    params = {"version": "2.1", "limit": max_results, **active}
    data = http_client.get_json(NPI_URL, params)
    return [_flatten_result(r) for r in data.get("results", [])]


def _flatten_result(r: dict[str, Any]) -> dict[str, Any]:
    basic = r.get("basic", {}) or {}
    taxonomies = r.get("taxonomies", []) or []
    addresses = r.get("addresses", []) or []

    primary_tax = next(
        (t for t in taxonomies if t.get("primary")), taxonomies[0] if taxonomies else {}
    )
    location = next(
        (a for a in addresses if a.get("address_purpose") == "LOCATION"),
        addresses[0] if addresses else {},
    )
    name_parts = [
        basic.get("name_prefix"),
        basic.get("first_name"),
        basic.get("last_name") or basic.get("organization_name"),
        basic.get("credential"),
    ]
    return {
        "npi": r.get("number", ""),
        "name": " ".join(p for p in name_parts if p),
        "specialty": primary_tax.get("desc", ""),
        "address": location.get("address_1", ""),
        "city": location.get("city", ""),
        "state": location.get("state", ""),
        "postal_code": location.get("postal_code", ""),
    }
