from pathlib import Path
from src.utils.logger import get_logger
from src.voice.text_to_speech import speak
from src.services.audio_service import AudioService
from src.models.request_context import RequestContext

logger = get_logger("tts_service")

class TTSService:
    """Service layer class orchestrating text-to-speech generation and playback."""
    
    def __init__(self, audio_service: AudioService = None):
        self.audio_service = audio_service or AudioService()
        
    def say(self, text: str, context: RequestContext = None) -> None:
        """
        Generates speech for the given text and plays it synchronously using the AudioService.
        
        Args:
            text: The text to speak.
            context: The request context for recording timings.
        """
        try:
            # Generate the cached or new MP3 file path
            if context: context.diagnostics.start_timer("TTS")
            mp3_path = speak(text)
            if context: context.diagnostics.stop_timer("TTS")
            
            # Delegate to AudioService for playback
            if context: context.diagnostics.start_timer("Playback")
            self.audio_service.play_file(mp3_path)
            if context: context.diagnostics.stop_timer("Playback")
        except Exception as e:
            logger.error(f"Error in TTSService.say(): {e}")
