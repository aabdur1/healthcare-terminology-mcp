# tests/test_rxnorm.py
import pytest

import rxnorm


def test_search_rxnorm_dedupes_and_caps(fake_responses):
    fake_responses[f"{rxnorm.RXNORM_BASE}/approximateTerm.json"] = {
        "approximateGroup": {
            "candidate": [
                {"rxcui": "6809", "score": "11.2"},
                {"rxcui": "6809", "score": "10.0"},
                {"rxcui": "1545653", "score": "9.5"},
                {"rxcui": "1234", "score": "8.0"},
            ]
        }
    }
    fake_responses[f"{rxnorm.RXNORM_BASE}/rxcui/6809/properties.json"] = {
        "properties": {"name": "metformin"}
    }
    fake_responses[f"{rxnorm.RXNORM_BASE}/rxcui/1545653/properties.json"] = {
        "properties": {"name": "metFORMIN extended release"}
    }

    results = rxnorm.search_rxnorm("metformin", max_results=2)

    assert results == [
        {"rxcui": "6809", "name": "metformin", "score": 11.2},
        {"rxcui": "1545653", "name": "metFORMIN extended release", "score": 9.5},
    ]


def test_search_rxnorm_skips_candidates_without_rxcui(fake_responses):
    fake_responses[f"{rxnorm.RXNORM_BASE}/approximateTerm.json"] = {
        "approximateGroup": {
            "candidate": [
                {"score": "5.0"},
                {"rxcui": "6809", "score": "11.2"},
            ]
        }
    }
    fake_responses[f"{rxnorm.RXNORM_BASE}/rxcui/6809/properties.json"] = {
        "properties": {"name": "metformin"}
    }

    assert rxnorm.search_rxnorm("metformin") == [
        {"rxcui": "6809", "name": "metformin", "score": 11.2}
    ]


def test_search_rxnorm_handles_no_candidates(fake_responses):
    fake_responses[f"{rxnorm.RXNORM_BASE}/approximateTerm.json"] = {
        "approximateGroup": {}
    }
    assert rxnorm.search_rxnorm("nope") == []


def test_search_rxnorm_rejects_blank_query():
    with pytest.raises(ValueError, match="drug_name cannot be empty"):
        rxnorm.search_rxnorm("  ")
