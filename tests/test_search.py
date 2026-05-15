import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import main


@pytest.fixture
def fake_responses(monkeypatch):
    """Replace _get_json with a lookup table keyed by URL."""
    responses: dict[str, object] = {}

    def fake_get(url, params):
        if url not in responses:
            raise AssertionError(f"unexpected URL: {url} (params={params})")
        value = responses[url]
        return value(params) if callable(value) else value

    monkeypatch.setattr(main, "_get_json", fake_get)
    return responses


# --------------------------------------------------------------------- ICD-10


def test_search_icd10_parses_rows(fake_responses):
    fake_responses[main.ICD10_URL] = [
        2,
        ["N18.9", "I12.9"],
        None,
        [
            ["N18.9", "Chronic kidney disease, unspecified"],
            ["I12.9", "Hypertensive chronic kidney disease"],
        ],
    ]

    results = main.search_icd10("kidney disease", max_results=10)

    assert results == [
        {"code": "N18.9", "description": "Chronic kidney disease, unspecified"},
        {"code": "I12.9", "description": "Hypertensive chronic kidney disease"},
    ]


def test_search_icd10_empty_result(fake_responses):
    fake_responses[main.ICD10_URL] = [0, [], None, []]
    assert main.search_icd10("nonsense query") == []


def test_search_icd10_rejects_blank_query():
    with pytest.raises(ValueError, match="query cannot be empty"):
        main.search_icd10("   ")


# ---------------------------------------------------------------------- LOINC


def test_search_loinc_parses_rows(fake_responses):
    fake_responses[main.LOINC_URL] = [
        1,
        ["4548-4"],
        None,
        [["4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood", "Hemoglobin A1c", "Bld"]],
    ]

    results = main.search_loinc("hemoglobin a1c")

    assert results == [
        {
            "code": "4548-4",
            "long_common_name": "Hemoglobin A1c/Hemoglobin.total in Blood",
            "component": "Hemoglobin A1c",
            "system": "Bld",
        }
    ]


def test_search_loinc_handles_short_row(fake_responses):
    fake_responses[main.LOINC_URL] = [1, ["X"], None, [["X", "name only"]]]

    results = main.search_loinc("x")

    assert results == [
        {"code": "X", "long_common_name": "name only", "component": "", "system": ""}
    ]


def test_search_loinc_rejects_blank_query():
    with pytest.raises(ValueError, match="query cannot be empty"):
        main.search_loinc("")


# --------------------------------------------------------------------- RxNorm


def test_search_rxnorm_dedupes_and_caps(fake_responses):
    fake_responses[f"{main.RXNORM_BASE}/approximateTerm.json"] = {
        "approximateGroup": {
            "candidate": [
                {"rxcui": "6809", "score": "11.2"},
                {"rxcui": "6809", "score": "10.0"},  # duplicate, should be skipped
                {"rxcui": "1545653", "score": "9.5"},
                {"rxcui": "1234", "score": "8.0"},  # past max_results=2
            ]
        }
    }
    fake_responses[f"{main.RXNORM_BASE}/rxcui/6809/properties.json"] = {
        "properties": {"name": "metformin"}
    }
    fake_responses[f"{main.RXNORM_BASE}/rxcui/1545653/properties.json"] = {
        "properties": {"name": "metFORMIN extended release"}
    }

    results = main.search_rxnorm("metformin", max_results=2)

    assert results == [
        {"rxcui": "6809", "name": "metformin", "score": 11.2},
        {"rxcui": "1545653", "name": "metFORMIN extended release", "score": 9.5},
    ]


def test_search_rxnorm_skips_candidates_without_rxcui(fake_responses):
    fake_responses[f"{main.RXNORM_BASE}/approximateTerm.json"] = {
        "approximateGroup": {
            "candidate": [
                {"score": "5.0"},  # no rxcui
                {"rxcui": "6809", "score": "11.2"},
            ]
        }
    }
    fake_responses[f"{main.RXNORM_BASE}/rxcui/6809/properties.json"] = {
        "properties": {"name": "metformin"}
    }

    results = main.search_rxnorm("metformin")

    assert results == [{"rxcui": "6809", "name": "metformin", "score": 11.2}]


def test_search_rxnorm_handles_no_candidates(fake_responses):
    fake_responses[f"{main.RXNORM_BASE}/approximateTerm.json"] = {
        "approximateGroup": {}
    }
    assert main.search_rxnorm("definitely-not-a-drug") == []


def test_search_rxnorm_rejects_blank_query():
    with pytest.raises(ValueError, match="drug_name cannot be empty"):
        main.search_rxnorm("  ")
