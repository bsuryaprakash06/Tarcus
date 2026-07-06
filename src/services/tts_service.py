from pathlib import Path
import queue
import threading
import re
from src.utils.logger import get_logger
from src.voice.text_to_speech import speak
from src.services.audio_service import AudioService
from src.models.request_context import RequestContext

logger = get_logger("tts_service")

class TTSService:
    """Service layer class orchestrating text-to-speech generation and playback."""
    
    def __init__(self, audio_service: AudioService = None):
        self.audio_service = audio_service or AudioService()
        self._stop_requested = threading.Event()
        
    def stop(self) -> None:
        """Interrupts playback and clears the queue."""
        logger.info("TTSService stop requested.")
        self._stop_requested.set()
        self.audio_service.stop()
        
    def say(self, text: str, context: RequestContext = None) -> None:
        """
        Generates speech for the given text. Splits multi-sentence text to pipeline 
        generation and playback for ultra-low latency.
        """
        self._stop_requested.clear()
        
        # Split text into sentences, preserving the punctuation
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        
        # If it's a very short response, execute synchronously
        if len(sentences) <= 1:
            try:
                if self._stop_requested.is_set(): return
                if context: context.diagnostics.start_timer("TTS")
                mp3_path = speak(text)
                if context: context.diagnostics.stop_timer("TTS")
                
                if self._stop_requested.is_set(): return
                if context: context.diagnostics.start_timer("Playback")
                self.audio_service.play_file(mp3_path)
                if context: context.diagnostics.stop_timer("Playback")
            except Exception as e:
                logger.error(f"Error in TTSService.say(): {e}")
            return
            
        # For multi-sentence responses, pipeline the generation!
        audio_queue = queue.Queue()
        
        def _generator_worker():
            for sentence in sentences:
                try:
                    mp3_path = speak(sentence)
                    audio_queue.put(mp3_path)
                except Exception as e:
                    logger.error(f"Failed to generate speech for sentence: {e}")
                    audio_queue.put(e)
            audio_queue.put(None) # Sentinel to close the queue
            
        # Start generator in the background
        if context: context.diagnostics.start_timer("TTS")
        threading.Thread(target=_generator_worker, daemon=True).start()
        
        first = True
        while True:
            if self._stop_requested.is_set():
                break
                
            try:
                item = audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue
                
            if item is None:
                break
                
            if isinstance(item, Exception):
                continue
                
            if first and context:
                context.diagnostics.stop_timer("TTS")
                context.diagnostics.start_timer("Playback")
                first = False
                
            try:
                self.audio_service.play_file(item)
            except Exception as e:
                logger.error(f"Error playing chunk: {e}")
                
        if not first and context:
            context.diagnostics.stop_timer("Playback")
