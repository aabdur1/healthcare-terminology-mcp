# tests/test_icd10.py
import pytest

import icd10


def test_search_icd10_parses_rows(fake_responses):
    fake_responses[icd10.ICD10_URL] = [
        2,
        ["N18.9", "I12.9"],
        None,
        [
            ["N18.9", "Chronic kidney disease, unspecified"],
            ["I12.9", "Hypertensive chronic kidney disease"],
        ],
    ]

    results = icd10.search_icd10("kidney disease", max_results=10)

    assert results == [
        {"code": "N18.9", "description": "Chronic kidney disease, unspecified"},
        {"code": "I12.9", "description": "Hypertensive chronic kidney disease"},
    ]


def test_search_icd10_empty_result(fake_responses):
    fake_responses[icd10.ICD10_URL] = [0, [], None, []]
    assert icd10.search_icd10("nonsense") == []


def test_search_icd10_rejects_blank_query():
    with pytest.raises(ValueError, match="query cannot be empty"):
        icd10.search_icd10("   ")


def test_expand_icd10_returns_subcodes(fake_responses):
    fake_responses[icd10.ICD10_URL] = [
        3,
        ["E11.0", "E11.1", "E11.9"],
        None,
        [
            ["E11.0", "Type 2 DM with hyperosmolarity"],
            ["E11.1", "Type 2 DM with ketoacidosis"],
            ["E11.9", "Type 2 DM without complications"],
        ],
    ]

    results = icd10.expand_icd10("E11")

    assert len(results) == 3
    assert all(r["code"].startswith("E11") for r in results)


def test_expand_icd10_rejects_blank():
    with pytest.raises(ValueError, match="prefix cannot be empty"):
        icd10.expand_icd10("")
