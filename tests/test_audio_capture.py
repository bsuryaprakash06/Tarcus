import pytest
import numpy as np
from src.audio.audio_capture_service import AudioCaptureService

def test_audio_capture_subscription():
    service = AudioCaptureService()
    # Reset for test
    service._subscribers.clear()
    
    q = service.subscribe("test_sub", queue_size=10)
    assert "test_sub" in service._subscribers
    assert q.maxsize == 10
    
    service.unsubscribe("test_sub")
    assert "test_sub" not in service._subscribers

def test_audio_capture_queue_behavior():
    service = AudioCaptureService()
    service._subscribers.clear()
    
    q = service.subscribe("test_sub", queue_size=2)
    
    # Simulate callbacks
    frame1 = np.array([1, 2, 3], dtype=np.int16)
    frame2 = np.array([4, 5, 6], dtype=np.int16)
    frame3 = np.array([7, 8, 9], dtype=np.int16)
    
    service._audio_callback(frame1, len(frame1), None, None)
    service._audio_callback(frame2, len(frame2), None, None)
    
    assert q.qsize() == 2
    
    # This should drop frame1 and push frame3 (ring buffer behavior)
    service._audio_callback(frame3, len(frame3), None, None)
    
    assert service.frames_dropped == 1
    
    # The oldest frame in the queue should now be frame2, and newest is frame3
    out1 = q.get_nowait()
    out2 = q.get_nowait()
    
    assert np.array_equal(out1, frame2)
    assert np.array_equal(out2, frame3)
