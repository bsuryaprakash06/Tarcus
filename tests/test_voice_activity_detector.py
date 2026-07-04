import pytest
import numpy as np
import time
from src.voice.voice_activity_detector import VoiceActivityDetector

def test_vad_speech_detection_and_continuation():
    vad = VoiceActivityDetector()
    vad.enabled = True
    vad.threshold = 0.5
    
    # Silence frame
    quiet_frame = np.array([[0, 0]], dtype=np.int16)
    vad.process_frame(quiet_frame)
    assert vad.speech_detected == False
    assert vad.first_speech_time is None
    
    # Speech frame (oscillating to avoid DC offset cancellation)
    loud_frame = np.array([[30000, -30000]], dtype=np.int16)
    vad.process_frame(loud_frame)
    assert vad.speech_detected == True
    assert vad.first_speech_time is not None
    assert vad.last_speech_time is not None

def test_vad_early_stopping():
    vad = VoiceActivityDetector()
    vad.enabled = True
    vad.silence_timeout = 0.5
    vad.min_speech = 0.5
    
    vad.start_time = time.time() - 2.0
    vad.speech_detected = True
    vad.first_speech_time = time.time() - 1.5
    vad.last_speech_time = time.time() - 0.6  # 0.6s silence > 0.5 timeout
    
    assert vad.should_continue() == False

def test_vad_false_silence_prevention():
    vad = VoiceActivityDetector()
    vad.enabled = True
    vad.silence_timeout = 0.5
    vad.min_speech = 1.0 # Requires at least 1.0s of speech before stopping
    
    vad.start_time = time.time() - 0.8 # We've only been recording for 0.8s
    vad.speech_detected = True
    vad.last_speech_time = time.time() - 0.6 # 0.6s of silence > 0.5 timeout
    
    # Even though silence timeout is reached, min_speech is not, so it shouldn't stop
    assert vad.should_continue() == True

def test_vad_maximum_recording_timeout():
    vad = VoiceActivityDetector()
    vad.enabled = True
    vad.max_duration = 10.0
    
    vad.start_time = time.time() - 10.1 # Exceeds max
    vad.speech_detected = True
    vad.last_speech_time = time.time() - 0.1 # Active speech
    
    # Must stop if max duration is hit, regardless of active speech
    assert vad.should_continue() == False
