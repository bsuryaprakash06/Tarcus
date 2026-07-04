import pytest
import numpy as np
import time
from src.voice.voice_activity_detector import VoiceActivityDetector
from src.utils import settings

def test_vad_initialization():
    vad = VoiceActivityDetector()
    assert vad.enabled == settings.VOICE_ACTIVITY_ENABLED
    assert vad.max_duration == settings.MAX_RECORDING_SECONDS

def test_vad_speech_detection():
    vad = VoiceActivityDetector()
    vad.enabled = True
    vad.threshold = 0.5
    
    # Simulate a loud frame
    loud_frame = np.array([[10000, 10000]], dtype=np.int16)
    vad.process_frame(loud_frame)
    
    # Using raw np array energy check
    # RMS of loud_frame is 10000.0 which is > 0.5
    assert vad.speech_detected == True

def test_vad_silence_timeout():
    vad = VoiceActivityDetector()
    vad.enabled = True
    vad.silence_timeout = 0.1
    vad.min_speech = 0.0 # Force immediate timeout eligibility
    
    vad.start_time = time.time() - 1.0
    vad.last_speech_time = time.time() - 0.5 # 0.5s of silence > 0.1s timeout
    
    assert vad.should_continue() == False
