# tests/test_batch.py
import pytest

import batch
import icd10


def test_batch_search_icd10_processes_multiple_queries(fake_responses):
    # Return different rows depending on which `terms` value the caller passes
    def icd10_response(params):
        if params["terms"] == "diabetes":
            return [1, ["E11.9"], None, [["E11.9", "Type 2 DM"]]]
        if params["terms"] == "pneumonia":
            return [1, ["J18.9"], None, [["J18.9", "Pneumonia, unspecified"]]]
        return [0, [], None, []]

    fake_responses[icd10.ICD10_URL] = icd10_response

    results = batch.batch_search_icd10(["diabetes", "pneumonia"], max_results_each=1)

    assert results == {
        "diabetes": [{"code": "E11.9", "description": "Type 2 DM"}],
        "pneumonia": [{"code": "J18.9", "description": "Pneumonia, unspecified"}],
    }


def test_batch_search_icd10_rejects_empty_list():
    with pytest.raises(ValueError, match="at least one"):
        batch.batch_search_icd10([])
