from typing import Optional, List
import numpy as np
from src.utils.logger import get_logger
from src.utils.settings import WAKE_PHRASES, WAKEWORD_CONFIDENCE
from .base import BaseWakeWordProvider, WakeDetectionResult

logger = get_logger("wakeword.openwakeword_provider")

class OpenWakeWordProvider(BaseWakeWordProvider):
    """OpenWakeWord based detector."""
    
    def __init__(self):
        try:
            import openwakeword
            from openwakeword.model import Model
            
            # Initialize openwakeword model
            openwakeword.utils.download_models()
            # openwakeword defaults to its pre-trained models. For "hey tarcus",
            # we might not have a pre-trained model. We will load the default 'hey_mycroft'
            # or 'alexa' as a stand-in, unless we have custom .onnx models.
            # In a real implementation, you'd specify custom model paths here.
            self.model = Model(
                wakeword_models=["hey_jarvis_v0.1"], # Fallback standard model for testing
                inference_framework="onnx"
            )
            logger.info("OpenWakeWordDetector initialized.")
        except ImportError:
            logger.error("openwakeword not installed. Please run `pip install openwakeword`")
            self.model = None

    def detect(self, audio_frame: np.ndarray) -> WakeDetectionResult:
        if self.model is None:
            return WakeDetectionResult(False)
            
        # OpenWakeWord expects 16-bit 16kHz numpy array
        prediction = self.model.predict(audio_frame)
        
        # Check if any model crossed the confidence threshold
        for mdl_name, scores in prediction.items():
            # openwakeword predict returns a list of scores or a single score per model
            # depending on internal chunking, but generally it's a float or list
            if isinstance(scores, list):
                score = scores[-1] if scores else 0.0
            else:
                score = scores
                
            if score >= WAKEWORD_CONFIDENCE:
                logger.info(f"Wake word '{mdl_name}' detected with confidence: {score:.3f}")
                # We map it to our configured WAKE_PHRASES[0] for semantic consistency
                phrase_name = WAKE_PHRASES[0] if WAKE_PHRASES else "hey tarcus"
                return WakeDetectionResult(True, phrase=phrase_name, confidence=score)
                
        return WakeDetectionResult(False)

class DummyWakeWordProvider(BaseWakeWordProvider):
    """A dummy detector that triggers periodically or via API for testing."""
    def __init__(self):
        self.counter = 0
        
    def detect(self, audio_frame: np.ndarray) -> WakeDetectionResult:
        # In a real testing scenario, we might trigger this via an external event.
        # For safety, it never automatically fires unless we set a flag.
        return WakeDetectionResult(False)
