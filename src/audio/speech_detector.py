import queue
import threading
import numpy as np
from src.providers.registry import ProviderRegistry
from src.utils.logger import get_logger

logger = get_logger("audio.speech_detector")

class SpeechDetector:
    """
    Subscribes to the AudioRouter and uses a VAD Provider to detect if speech is currently happening.
    """
    def __init__(self, provider_id: str = "silero"):
        self.provider = ProviderRegistry.create_provider("vad", provider_id)
        self.is_speaking = False
        
    def process_frame(self, frame: np.ndarray) -> bool:
        """
        Returns True if the current frame contains speech.
        """
        currently_speaking = self.provider.process_frame(frame)
        self.is_speaking = currently_speaking
        return currently_speaking
        
    def reset(self):
        self.is_speaking = False
        if hasattr(self.provider, "reset"):
            self.provider.reset()
