from abc import ABC, abstractmethod
import numpy as np

class WakeDetectionResult:
    def __init__(self, detected: bool, phrase: str = None, confidence: float = 0.0):
        self.detected = detected
        self.phrase = phrase
        self.confidence = confidence

class BaseWakeWordProvider(ABC):
    """Base interface for Wake Word detection."""
    
    @abstractmethod
    def detect(self, audio_frame: np.ndarray) -> WakeDetectionResult:
        """Process an audio frame and return detection result."""
        pass
