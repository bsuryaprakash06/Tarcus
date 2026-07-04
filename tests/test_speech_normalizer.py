import pytest
from src.normalization.speech_normalizer import SpeechNormalizer
from src.models.normalization import NormalizationCategory

@pytest.fixture
def normalizer():
    return SpeechNormalizer()

def test_normalization_applications(normalizer):
    res = normalizer.normalize("close not bad")
    assert res.normalized_text == "close Notepad"
    assert len(res.changes) == 1
    assert res.changes[0].category == NormalizationCategory.APPLICATION

def test_normalization_brands(normalizer):
    res = normalizer.normalize("search chat g p t")
    assert res.normalized_text == "search ChatGPT"
    assert len(res.changes) == 1
    assert res.changes[0].category == NormalizationCategory.BRAND

def test_normalization_technical_terms(normalizer):
    res = normalizer.normalize("create a vector data base")
    assert res.normalized_text == "create a vector database"
    assert len(res.changes) == 1
    assert res.changes[0].category == NormalizationCategory.TECHNICAL_TERM

def test_normalization_os_commands(normalizer):
    res = normalizer.normalize("open task manger")
    assert res.normalized_text == "open Task Manager"
    assert len(res.changes) == 1
    assert res.changes[0].category == NormalizationCategory.OS_COMMAND

def test_unrelated_sentences_unchanged(normalizer):
    text = "What is an embedding"
    res = normalizer.normalize(text)
    # "embedding" is in our dict mapping to "embedding", so the text doesn't structurally change 
    # and no modification is recorded.
    assert res.normalized_text == text
    assert len(res.changes) == 0
    assert res.confidence == 1.0

def test_word_boundaries_prevent_partial_matches(normalizer):
    text = "how to calculate the sum"
    res = normalizer.normalize(text)
    # "calc" is in the dict mapping to "Calculator", but it should NOT match inside "calculate"
    assert res.normalized_text == text
    assert len(res.changes) == 0

def test_case_preservation(normalizer):
    res = normalizer.normalize("Open note pad")
    # Only "note pad" is replaced with "Notepad". "Open" remains unchanged.
    assert res.normalized_text == "Open Notepad"
    
def test_longest_match(normalizer):
    res = normalizer.normalize("open visual studio code")
    # "vs code" and "visual studio code" both map to "VS Code".
    # Should correctly match the entire 3-word phrase.
    assert res.normalized_text == "open VS Code"

def test_user_dictionary_overrides(normalizer):
    # Using the config/user_dictionary.json we created
    res = normalizer.normalize("open tarkus")
    assert res.normalized_text == "open Tarcus"
    assert len(res.changes) == 1
    assert res.changes[0].category == NormalizationCategory.USER_DEFINED
