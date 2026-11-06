import pytest

from core import llm


def test_extract_json_plain():
    assert llm.extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_code_fence():
    assert llm.extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_surrounding_prose():
    assert llm.extract_json('Sure! {"a": {"b": 2}} Hope that helps.') == {"a": {"b": 2}}


def test_missing_token_gives_friendly_error(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(llm.LLMError, match="not configured"):
        llm.chat([{"role": "user", "content": "hi"}])


def test_fallback_model_dedupes(monkeypatch):
    monkeypatch.setenv("MODEL_ID", "x/y")
    monkeypatch.setenv("MODEL_FALLBACK", "x/y")
    assert llm.models() == ["x/y"]
