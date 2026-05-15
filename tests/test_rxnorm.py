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


def test_ndc_to_rxcui_returns_rxcui(fake_responses):
    fake_responses[f"{rxnorm.RXNORM_BASE}/rxcui.json"] = {
        "idGroup": {"rxnormId": ["860975"]}
    }

    result = rxnorm.ndc_to_rxcui("00378-0518-77")
    assert result == {"ndc": "00378-0518-77", "rxcui": "860975"}


def test_ndc_to_rxcui_handles_no_match(fake_responses):
    fake_responses[f"{rxnorm.RXNORM_BASE}/rxcui.json"] = {"idGroup": {}}

    result = rxnorm.ndc_to_rxcui("99999-9999-99")
    assert result == {"ndc": "99999-9999-99", "rxcui": None}


def test_rxcui_to_ndcs_returns_list(fake_responses):
    fake_responses[f"{rxnorm.RXNORM_BASE}/rxcui/6809/ndcs.json"] = {
        "ndcGroup": {"ndcList": {"ndc": ["00093-1074-01", "00093-1074-05"]}}
    }

    result = rxnorm.rxcui_to_ndcs("6809")
    assert result == {"rxcui": "6809", "ndcs": ["00093-1074-01", "00093-1074-05"]}


def test_rxcui_to_ndcs_handles_no_ndcs(fake_responses):
    fake_responses[f"{rxnorm.RXNORM_BASE}/rxcui/9999999/ndcs.json"] = {"ndcGroup": {}}

    result = rxnorm.rxcui_to_ndcs("9999999")
    assert result == {"rxcui": "9999999", "ndcs": []}
