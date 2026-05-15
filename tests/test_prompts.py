# tests/test_prompts.py
import prompts


def test_code_chart_note_includes_input():
    result = prompts.code_chart_note(
        chart_note="65yo M with type 2 diabetes on metformin, A1c 8.2"
    )
    assert "type 2 diabetes" in result
    assert "search_icd10" in result
    assert "search_rxnorm" in result
    assert "search_loinc" in result


def test_summarize_med_list_includes_rxcuis():
    result = prompts.summarize_med_list(rxcuis=["6809", "153165"])
    assert "6809" in result
    assert "153165" in result
    assert "rxcui_to_ndcs" in result
