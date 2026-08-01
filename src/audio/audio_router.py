import queue
import threading
from typing import Dict
import numpy as np
from src.utils.logger import get_logger

logger = get_logger("audio.router")

class AudioRouter:
    """
    Distributes raw audio frames from the Capture Service to various consumers.
    """
    def __init__(self, capture_service):
        self.capture_service = capture_service
        self._subscribers: Dict[str, queue.Queue] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self._input_queue = None

    def start(self):
        if self._running: return
        self._running = True
        self._input_queue = self.capture_service.subscribe("router")
        self._thread = threading.Thread(target=self._route_loop, daemon=True, name="AudioRouter")
        self._thread.start()
        logger.info("AudioRouter started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._input_queue:
            self.capture_service.unsubscribe("router")
        logger.info("AudioRouter stopped.")

    def subscribe(self, name: str, queue_size: int = 100) -> queue.Queue:
        with self._lock:
            q = queue.Queue(maxsize=queue_size)
            self._subscribers[name] = q
            logger.debug(f"AudioRouter subscriber added: {name}")
            return q

    def unsubscribe(self, name: str):
        with self._lock:
            if name in self._subscribers:
                del self._subscribers[name]
                logger.debug(f"AudioRouter subscriber removed: {name}")

    def _route_loop(self):
        while self._running:
            try:
                frame = self._input_queue.get(timeout=0.1)
                
                with self._lock:
                    for name, q in self._subscribers.items():
                        try:
                            # Non-blocking put to avoid one slow subscriber blocking others
                            q.put_nowait(frame.copy())
                        except queue.Full:
                            # Drop frame for this specific subscriber if its queue is full
                            pass
                            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in AudioRouter: {e}")
