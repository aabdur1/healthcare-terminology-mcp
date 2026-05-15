# tests/test_icd10.py
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
    import pytest
    with pytest.raises(ValueError, match="query cannot be empty"):
        icd10.search_icd10("   ")
