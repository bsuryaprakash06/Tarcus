import threading
import queue
import time
import numpy as np
from src.audio.audio_capture_service import AudioCaptureService
from src.wakeword.wakeword_detector import WakeWordDetector, OpenWakeWordDetector, DummyDetector
from src.utils.settings import WAKEWORD_PROVIDER, ENABLE_WAKEWORD
from src.utils.logger import get_logger
from src.events.pipeline_events import PipelineEventBus
from src.wakeword.wakeword_events import WakeWordDetected

logger = get_logger("wakeword.passive_listener")

class PassiveListener:
    """
    Runs continuously on a background thread. Reads from the AudioCaptureService
    and feeds frames into the WakeWordDetector. Emits a WakeWordDetected event on success.
    """
    def __init__(self, audio_service: AudioCaptureService):
        self.audio_service = audio_service
        self.event_bus = PipelineEventBus()
        self._thread = None
        self._stop_event = threading.Event()
        self._audio_queue = None
        self._detector = self._initialize_detector()
        
    def _initialize_detector(self) -> WakeWordDetector:
        if WAKEWORD_PROVIDER.lower() == "openwakeword":
            return OpenWakeWordDetector()
        return DummyDetector()

    def start(self):
        if not ENABLE_WAKEWORD:
            logger.info("Wake word detection is disabled in settings.")
            return
            
        if self._thread and self._thread.is_alive():
            return
            
        self._stop_event.clear()
        self._audio_queue = self.audio_service.subscribe("passive_listener")
        self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="PassiveListenerThread")
        self._thread.start()
        logger.info("PassiveListener started.")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._audio_queue:
            self.audio_service.unsubscribe("passive_listener")
            self._audio_queue = None
        logger.info("PassiveListener stopped.")

    def _listen_loop(self):
        # OpenWakeWord expects 1280 samples per prediction usually (80ms at 16kHz)
        # We'll buffer chunks from the queue until we have enough to feed it
        buffer = np.array([], dtype=np.int16)
        
        while not self._stop_event.is_set():
            try:
                frame = self._audio_queue.get(timeout=0.1)
                buffer = np.concatenate((buffer, frame))
                
                # If we have at least 1280 samples, feed it to the detector
                # You can tune chunk_size based on what the detector prefers.
                chunk_size = 1280
                while len(buffer) >= chunk_size:
                    chunk = buffer[:chunk_size]
                    buffer = buffer[chunk_size:]
                    
                    result = self._detector.detect(chunk)
                    if result.detected:
                        # Clear buffer to avoid double triggers
                        buffer = np.array([], dtype=np.int16)
                        
                        # Emit event
                        self.event_bus.publish_event(WakeWordDetected(phrase=result.phrase))
                        
                        # Optional: Sleep briefly to avoid rapid double-triggers
                        time.sleep(1.0)
                        
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in PassiveListener loop: {e}")
                time.sleep(1.0)
