import pytest
from unittest.mock import patch, MagicMock
from src.routing.classifier import IntentClassifier
from src.routing.router import IntentRouter
from src.routing.intent import Intent
from src.providers.base_provider import ProviderResponse
import json

@pytest.fixture
def mock_provider():
    # We patch inside the classifier module where it's imported
    with patch("src.routing.classifier.get_provider_from_settings") as mock_factory:
        provider = MagicMock()
        mock_factory.return_value = provider
        yield provider

def test_classifier_parses_clean_json(mock_provider):
    mock_provider.generate.return_value = ProviderResponse(
        text='{"intent": "AUTOMATION", "confidence": 0.98, "reason": "App launch command"}',
        model_name="mock", provider_name="mock", latency=0.1
    )
    classifier = IntentClassifier()
    result = classifier.classify("open notepad")
    
    assert result.intent == Intent.AUTOMATION
    assert result.confidence == 0.98
    
def test_classifier_strips_markdown(mock_provider):
    # LLMs frequently hallucinate markdown wrappers around JSON
    mock_provider.generate.return_value = ProviderResponse(
        text='```json\n{"intent": "LLM_CHAT", "confidence": 0.95, "reason": "Question"}\n```',
        model_name="mock", provider_name="mock", latency=0.1
    )
    classifier = IntentClassifier()
    result = classifier.classify("what is an embedding")
    
    assert result.intent == Intent.LLM_CHAT
    assert result.confidence == 0.95

def test_classifier_retries_on_invalid_schema(mock_provider):
    # First attempt: complete garbage
    # Second attempt: valid JSON
    mock_provider.generate.side_effect = [
        ProviderResponse(text="Sure! Here is the JSON: \n { bad json", model_name="mock", provider_name="mock", latency=0.1),
        ProviderResponse(text='{"intent": "CONVERSATION", "confidence": 0.99, "reason": "Greeting"}', model_name="mock", provider_name="mock", latency=0.1)
    ]
    classifier = IntentClassifier()
    result = classifier.classify("hello")
    
    assert result.intent == Intent.CONVERSATION
    assert mock_provider.generate.call_count == 2

def test_router_destination_mapping(mock_provider):
    mock_provider.generate.return_value = ProviderResponse(
        text='{"intent": "CONVERSATION", "confidence": 0.99, "reason": "Greeting"}',
        model_name="mock", provider_name="mock", latency=0.1
    )
    router = IntentRouter()
    result = router.route("Hello there")
    
    assert result.intent == Intent.CONVERSATION
    assert result.destination == "ConversationService"

def test_router_low_confidence_fallback(mock_provider):
    mock_provider.generate.return_value = ProviderResponse(
        text='{"intent": "AUTOMATION", "confidence": 0.40, "reason": "Too ambiguous"}',
        model_name="mock", provider_name="mock", latency=0.1
    )
    router = IntentRouter()
    result = router.route("do something with that text app")
    
    # Even though intent is AUTOMATION, confidence < 0.60 forces fallback
    assert result.destination == "FallbackService"

def test_router_mixed_intent_fallback(mock_provider):
    mock_provider.generate.return_value = ProviderResponse(
        text='{"intent": "MIXED", "confidence": 0.98, "reason": "Multi-task"}',
        model_name="mock", provider_name="mock", latency=0.1
    )
    router = IntentRouter()
    result = router.route("open calculator and explain what RAM is")
    
    assert result.intent == Intent.MIXED
    assert result.destination == "FallbackService"
