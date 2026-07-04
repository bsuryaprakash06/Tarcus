import pytest
from src.models.response import ResponseProfile, ResponseMode
from src.response.formatter import ResponseFormatter
from src.response.speech_optimizer import SpeechOptimizer

def test_speech_optimizer_spacing():
    # Should collapse multiple spaces and ensure proper spacing after punctuation
    raw = "Hello   world!  How are you? I'm good."
    optimized = SpeechOptimizer.optimize(raw)
    assert optimized == "Hello world! How are you? I'm good."
    
def test_speech_optimizer_leaves_commas():
    # Punctuation formatting should remain grammatically correct
    raw = "GitHub, Docker, and Kubernetes"
    optimized = SpeechOptimizer.optimize(raw)
    assert optimized == "GitHub, Docker, and Kubernetes"

def test_formatter_caching():
    formatter = ResponseFormatter()
    profile = ResponseProfile(mode=ResponseMode.KNOWLEDGE)
    raw = "An embedding is a numerical vector."
    
    # First call formats and caches
    r1 = formatter.format(raw, profile)
    
    # Extract cache key and intentionally poison the cached object's duration
    assert len(formatter._cache) == 1
    key = list(formatter._cache.keys())[0]
    formatter._cache[key].estimated_duration = 999.0
    
    # Second call should return the modified cached object
    r2 = formatter.format(raw, profile)
    assert r2.estimated_duration == 999.0
    
def test_formatter_no_cache_for_automation():
    formatter = ResponseFormatter()
    profile = ResponseProfile(mode=ResponseMode.AUTOMATION)
    raw = "Opening Notepad"
    
    # Automation should never cache
    r1 = formatter.format(raw, profile)
    assert len(formatter._cache) == 0
    
def test_formatter_duration_estimation():
    formatter = ResponseFormatter()
    profile = ResponseProfile(mode=ResponseMode.CONVERSATION)
    
    # 5 words -> expected 5 / 2.5 = 2.0 seconds
    raw = "This is a five word."
    r1 = formatter.format(raw, profile)
    assert r1.estimated_duration == 2.0

def test_formatter_ssml_prep():
    formatter = ResponseFormatter()
    profile = ResponseProfile(mode=ResponseMode.CONVERSATION)
    
    raw = "Hello"
    r1 = formatter.format(raw, profile)
    assert r1.ssml == "<speak>Hello</speak>"
