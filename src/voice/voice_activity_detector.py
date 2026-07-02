import time
import numpy as np
from src.utils.settings import (
    SILENCE_TIMEOUT_SECONDS,
    MAX_RECORDING_SECONDS,
    MIN_SPEECH_SECONDS,
    MIC_ENERGY_THRESHOLD,
    VOICE_ACTIVITY_ENABLED
)
from src.utils.logger import get_logger

logger = get_logger("voice.vad")

class VoiceActivityDetector:
    """
    A lightweight, stateless-like Voice Activity Detector (VAD) that analyzes 
    audio frames using numpy RMS energy calculations to determine if recording should continue.
    """
    def __init__(self):
        self.start_time = time.time()
        self.last_speech_time = self.start_time
        self.speech_detected = False
        
        # Pull latest settings
        self.enabled = VOICE_ACTIVITY_ENABLED
        self.max_duration = MAX_RECORDING_SECONDS
        self.silence_timeout = SILENCE_TIMEOUT_SECONDS
        self.min_speech = MIN_SPEECH_SECONDS
        self.threshold = MIC_ENERGY_THRESHOLD
        
        if self.enabled:
            logger.info(f"VAD Initialized (Threshold: {self.threshold}, Silence Timeout: {self.silence_timeout}s)")

    def process_frame(self, indata: np.ndarray) -> None:
        """
        Calculates the energy of the current audio frame and updates internal VAD state.
        
        Args:
            indata: A numpy array representing the audio frame from sounddevice.
        """
        if not self.enabled:
            return
            
        # Calculate RMS energy of the frame
        rms_energy = np.sqrt(np.mean(np.square(indata)))
        
        if rms_energy > self.threshold:
            self.last_speech_time = time.time()
            if not self.speech_detected:
                logger.info("Speech detected. Keeping stream alive...")
            self.speech_detected = True

    def should_continue(self) -> bool:
        """
        Evaluates the current state against timeouts to determine if recording should halt.
        
        Returns:
            True if the stream should keep recording, False to stop.
        """
        current_duration = time.time() - self.start_time
        
        # Rule 1: Never exceed max duration
        if current_duration >= self.max_duration:
            logger.info(f"Max recording duration ({self.max_duration}s) reached.")
            return False
            
        # Rule 2: If VAD is disabled, we just wait until max duration
        if not self.enabled:
            return True
            
        # Rule 3: Dynamic silence timeout
        # Only stop if we've recorded at least the minimum speech duration
        if current_duration > self.min_speech:
            silence_duration = time.time() - self.last_speech_time
            if silence_duration >= self.silence_timeout:
                if self.speech_detected:
                    logger.info(f"Silence timeout ({self.silence_timeout}s) reached. Stopping recording.")
                else:
                    logger.info("No speech detected within initial timeout window.")
                return False
                
        return True
