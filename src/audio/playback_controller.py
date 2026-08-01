import queue
import threading
import sounddevice as sd
import numpy as np
from typing import Optional
from src.utils.logger import get_logger
from src.events.pipeline_events import PipelineEventBus
from src.audio.audio_events import PlaybackStarted, PlaybackStopped, PlaybackInterrupted, PlaybackCompleted

logger = get_logger("audio.playback")

class PlaybackController:
    """
    Single source of truth for all system audio output.
    Supports play, queue, interrupt, fade_out.
    """
    def __init__(self):
        self.event_bus = PipelineEventBus()
        self._queue = queue.Queue()
        self._lock = threading.Lock()
        
        self._is_playing = False
        self._current_source = None
        self._stop_requested = False
        self._stream = None
        
        self._worker_thread = threading.Thread(target=self._playback_loop, daemon=True, name="PlaybackWorker")
        self._worker_thread.start()

    def play(self, audio_data: np.ndarray, source: str = "tts", sample_rate: int = 16000, wait: bool = False):
        """Immediately interrupt current playback and play new audio."""
        self.interrupt()
        self.queue(audio_data, source, sample_rate)
        
        if wait:
            # Simple spin-wait for completion
            import time
            while self.is_playing():
                time.sleep(0.1)

    def queue(self, audio_data: np.ndarray, source: str = "tts", sample_rate: int = 16000):
        """Add audio to the playback queue."""
        self._queue.put((audio_data, source, sample_rate))
        logger.debug(f"Queued audio from source '{source}'")

    def interrupt(self):
        """Instantly halt current playback and clear the queue."""
        with self._lock:
            self._stop_requested = True
            if self._stream and self._stream.active:
                self._stream.stop()
            self.clear_queue()
        logger.info("Playback interrupted.")
        self.event_bus.publish_event(PlaybackInterrupted())

    def fade_out(self, duration_ms: int = 500):
        """Smoothly fade out current playback."""
        # TODO: Implement dynamic volume fading logic in stream callback
        self.interrupt()

    def stop(self):
        """Halt playback and clear queue (alias for interrupt for simpler APIs)."""
        self.interrupt()

    def clear_queue(self):
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def is_playing(self) -> bool:
        return self._is_playing

    def current_source(self) -> Optional[str]:
        return self._current_source

    def _playback_loop(self):
        while True:
            try:
                audio_data, source, sr = self._queue.get(block=True)
                
                with self._lock:
                    self._stop_requested = False
                    self._is_playing = True
                    self._current_source = source
                    
                self.event_bus.publish_event(PlaybackStarted(source=source))
                logger.info(f"Playback started for source: {source}")
                
                # Setup output stream
                def callback(outdata, frames, time, status):
                    if status: logger.warning(status)
                    if self._stop_requested:
                        raise sd.CallbackStop()

                try:
                    with self._lock:
                        self._stream = sd.OutputStream(
                            samplerate=sr,
                            channels=1,
                            dtype='float32', # or int16 depending on inputs
                            callback=None # simple blocking play for now to manage state
                        )
                        self._stream.start()
                    
                    # Instead of a callback, we just write the data which blocks until done
                    if not self._stop_requested:
                        self._stream.write(audio_data)
                        
                except sd.CallbackStop:
                    pass
                except Exception as e:
                    logger.error(f"Playback error: {e}")
                finally:
                    with self._lock:
                        if self._stream:
                            self._stream.stop()
                            self._stream.close()
                            self._stream = None
                
                with self._lock:
                    self._is_playing = False
                    self._current_source = None
                    
                if self._stop_requested:
                    self.event_bus.publish_event(PlaybackStopped(filepath=None))
                else:
                    self.event_bus.publish_event(PlaybackCompleted())
                    logger.info("Playback completed naturally.")
                    
                self._queue.task_done()
                
            except Exception as e:
                logger.error(f"Playback worker error: {e}")
                import time
                time.sleep(1)
