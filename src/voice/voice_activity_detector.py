import time
import numpy as np
from src.utils.settings import (
    SILENCE_TIMEOUT_SECONDS,
    MAX_RECORDING_SECONDS,
    MIN_SPEECH_SECONDS,
    MIC_ENERGY_THRESHOLD,
    VOICE_ACTIVITY_ENABLED,
    INITIAL_SILENCE_TIMEOUT
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
        self.first_speech_time = None
        self.last_speech_time = None
        self.speech_detected = False
        self.current_state = "IDLE"
        
        # Pull latest settings
        self.enabled = VOICE_ACTIVITY_ENABLED
        self.max_duration = MAX_RECORDING_SECONDS
        self.silence_timeout = SILENCE_TIMEOUT_SECONDS
        self.initial_timeout = INITIAL_SILENCE_TIMEOUT
        self.min_speech = MIN_SPEECH_SECONDS
        self.threshold = MIC_ENERGY_THRESHOLD
        
        if self.enabled:
            logger.info(f"VAD Initialized (Threshold: {self.threshold}, Silence: {self.silence_timeout}s, Initial: {self.initial_timeout}s)")

    def process_frame(self, indata: np.ndarray) -> None:
        """
        Calculates the energy of the current audio frame and updates internal VAD state.
        
        Args:
            indata: A numpy array representing the audio frame from sounddevice.
        """
        if not self.enabled:
            return
            
        # Normalize audio to [-1.0, 1.0] and remove DC offset
        normalized_audio = indata.astype(np.float32) / 32768.0
        normalized_audio -= np.mean(normalized_audio)
        
        # Calculate RMS energy
        rms_energy = np.sqrt(np.mean(np.square(normalized_audio)))
        
        is_speech_frame = rms_energy > self.threshold
        current_time = time.time()
        
        if is_speech_frame:
            self.last_speech_time = current_time
            if not self.speech_detected:
                self.first_speech_time = current_time
                self.speech_detected = True
            new_state = "SPEAKING"
        else:
            if self.speech_detected:
                new_state = "SILENCE"
            else:
                new_state = "IDLE"
                
        # State transition logger
        if new_state != self.current_state:
            first_str = f"{self.first_speech_time:.2f}" if self.first_speech_time else "None"
            last_str = f"{self.last_speech_time:.2f}" if self.last_speech_time else "None"
            silence_start = f"{self.last_speech_time:.2f}" if new_state == "SILENCE" and self.last_speech_time else "N/A"
            
            logger.info(
                f"VAD State: {self.current_state} -> {new_state} | "
                f"Energy: {rms_energy:.4f} | "
                f"Threshold: {self.threshold} | "
                f"First: {first_str} | "
                f"Last: {last_str} | "
                f"Silence Start: {silence_start}"
            )
            self.current_state = new_state

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
        if not self.speech_detected:
            # Give the user more time to start speaking
            if current_duration >= self.initial_timeout:
                logger.info(f"No speech detected within initial timeout ({self.initial_timeout}s). Stopping.")
                return False
        else:
            # Trailing silence timeout
            if current_duration > self.min_speech and self.last_speech_time is not None:
                silence_duration = time.time() - self.last_speech_time
                if silence_duration >= self.silence_timeout:
                    logger.info(f"Silence timeout ({self.silence_timeout}s) reached. Stopping recording.")
                    return False
                
        return True
