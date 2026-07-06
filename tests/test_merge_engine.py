import pytest
from src.dialogue.merge_engine import HybridMergeEngine

def test_deterministic_merge():
    engine = HybridMergeEngine()
    
    # Simple substitution
    assert engine._deterministic_merge("Close it.", "Notepad") == "Close Notepad."
    assert engine._deterministic_merge("Delete it.", "notes.txt") == "Delete notes.txt."
    assert engine._deterministic_merge("Close the first one.", "Notepad") == "Close Notepad."
    
    # Reject complex replies (force LLM fallback)
    assert engine._deterministic_merge("Close it.", "Actually I meant Calculator") is None
    assert engine._deterministic_merge("Rename it.", "nevermind") is None
    
def test_hybrid_merge_fast_path():
    engine = HybridMergeEngine()
    
    # Should use fast path and succeed without an LLM call
    assert engine.merge("Open it.", "Discord") == "Open Discord."
