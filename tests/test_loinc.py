# tests/test_loinc.py
import pytest

import loinc


def test_search_loinc_parses_rows(fake_responses):
    fake_responses[loinc.LOINC_URL] = [
        1,
        ["4548-4"],
        None,
        [["4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood", "Hemoglobin A1c", "Bld"]],
    ]

    results = loinc.search_loinc("hemoglobin a1c")

    assert results == [
        {
            "code": "4548-4",
            "long_common_name": "Hemoglobin A1c/Hemoglobin.total in Blood",
            "component": "Hemoglobin A1c",
            "system": "Bld",
        }
    ]


def test_search_loinc_handles_short_row(fake_responses):
    fake_responses[loinc.LOINC_URL] = [1, ["X"], None, [["X", "name only"]]]

    assert loinc.search_loinc("x") == [
        {"code": "X", "long_common_name": "name only", "component": "", "system": ""}
    ]


def test_search_loinc_rejects_blank_query():
    with pytest.raises(ValueError, match="query cannot be empty"):
        loinc.search_loinc("")
