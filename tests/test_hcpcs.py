# tests/test_hcpcs.py
import pytest

import hcpcs


def test_search_hcpcs_parses_rows(fake_responses):
    fake_responses[hcpcs.HCPCS_URL] = [
        1,
        ["J1100"],
        None,
        [["J1100", "Injection, dexamethasone sodium phosphate, 1 mg"]],
    ]

    results = hcpcs.search_hcpcs("dexamethasone injection")
    assert results == [
        {
            "code": "J1100",
            "description": "Injection, dexamethasone sodium phosphate, 1 mg",
        }
    ]


def test_search_hcpcs_rejects_blank():
    with pytest.raises(ValueError, match="query cannot be empty"):
        hcpcs.search_hcpcs("")
