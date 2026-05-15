# tests/test_npi.py
import pytest

import npi


def test_search_npi_by_number(fake_responses):
    fake_responses[npi.NPI_URL] = {
        "result_count": 1,
        "results": [
            {
                "number": "1234567890",
                "basic": {
                    "name_prefix": "Dr.",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "credential": "MD",
                },
                "taxonomies": [{"desc": "Internal Medicine", "primary": True}],
                "addresses": [
                    {
                        "address_purpose": "LOCATION",
                        "address_1": "123 Main St",
                        "city": "Chicago",
                        "state": "IL",
                        "postal_code": "60601",
                    }
                ],
            }
        ],
    }

    results = npi.search_npi(npi_number="1234567890")
    assert len(results) == 1
    assert results[0]["npi"] == "1234567890"
    assert results[0]["name"] == "Dr. Jane Doe MD"
    assert results[0]["specialty"] == "Internal Medicine"
    assert results[0]["city"] == "Chicago"
    assert results[0]["state"] == "IL"


def test_search_npi_by_name(fake_responses):
    fake_responses[npi.NPI_URL] = {
        "result_count": 0,
        "results": [],
    }
    assert npi.search_npi(last_name="Nobody") == []


def test_search_npi_requires_some_field():
    with pytest.raises(ValueError, match="at least one"):
        npi.search_npi()
