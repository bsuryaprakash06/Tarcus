import pytest
import numpy as np
from src.wakeword.wakeword_detector import DummyDetector

def test_dummy_detector():
    detector = DummyDetector()
    frame = np.zeros(1280, dtype=np.int16)
    
    # Dummy detector should always return False by default
    result = detector.detect(frame)
    assert result.detected is False
    assert result.phrase is None
