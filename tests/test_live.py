# tests/test_live.py
import pytest

import http_client
import icd10
import loinc
import rxnorm

pytestmark = pytest.mark.live


@pytest.fixture(autouse=True)
def _clear_cache():
    """Force every live test to hit the real network, not the lru_cache."""
    http_client.clear_cache()
    yield


def test_icd10_live_lookup():
    results = icd10.search_icd10("type 2 diabetes", max_results=3)
    assert len(results) >= 1
    assert all("code" in r and "description" in r for r in results)


def test_loinc_live_lookup():
    results = loinc.search_loinc("hemoglobin a1c", max_results=3)
    assert len(results) >= 1
    assert all("code" in r for r in results)


def test_rxnorm_live_lookup():
    results = rxnorm.search_rxnorm("metformin", max_results=3)
    assert len(results) >= 1
    assert results[0]["name"]
