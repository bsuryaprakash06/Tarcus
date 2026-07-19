import queue
import threading
import numpy as np
import sounddevice as sd
from typing import Dict, Any, Callable
from src.utils.settings import SAMPLE_RATE, CHANNELS
from src.utils.logger import get_logger

logger = get_logger("audio.capture")

class AudioCaptureService:
    """
    Centralized owner of the microphone. 
    Continuously captures audio frames and distributes them to subscribers via thread-safe queues.
    This prevents multiple components from fighting over the microphone.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioCaptureService, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._lock = threading.Lock()
        self._subscribers: Dict[str, queue.Queue] = {}
        self._is_recording = False
        self._stream = None
        
        # Audio stats
        self.frames_captured = 0
        self.frames_dropped = 0

    def subscribe(self, subscriber_id: str, queue_size: int = 100) -> queue.Queue:
        """
        Registers a new subscriber and returns a Queue that will receive audio chunks.
        """
        with self._lock:
            if subscriber_id not in self._subscribers:
                q = queue.Queue(maxsize=queue_size)
                self._subscribers[subscriber_id] = q
                logger.info(f"Registered audio subscriber: {subscriber_id}")
                return q
            return self._subscribers[subscriber_id]

    def unsubscribe(self, subscriber_id: str):
        with self._lock:
            if subscriber_id in self._subscribers:
                del self._subscribers[subscriber_id]
                logger.info(f"Unregistered audio subscriber: {subscriber_id}")

    def start(self):
        with self._lock:
            if self._is_recording:
                return
                
            self._is_recording = True
            self.frames_captured = 0
            self.frames_dropped = 0
            
            logger.info("Starting AudioCaptureService microphone stream...")
            
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                callback=self._audio_callback
            )
            self._stream.start()

    def stop(self):
        with self._lock:
            if not self._is_recording:
                return
                
            logger.info("Stopping AudioCaptureService microphone stream...")
            self._is_recording = False
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            logger.warning(f"Audio stream status: {status}")
            
        frame_data = indata.copy()
        self.frames_captured += 1
        
        with self._lock:
            for sub_id, q in self._subscribers.items():
                try:
                    q.put_nowait(frame_data)
                except queue.Full:
                    self.frames_dropped += 1
                    # To prevent blocking the audio callback, we just drop the frame for this subscriber
                    # (In a real production app, we might want to pop the oldest and push the newest)
                    try:
                        q.get_nowait()
                        q.put_nowait(frame_data)
                    except Exception:
                        pass
