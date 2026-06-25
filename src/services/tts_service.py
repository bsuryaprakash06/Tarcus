from pathlib import Path
from src.utils.logger import get_logger
from src.voice.text_to_speech import speak
from src.services.audio_service import AudioService

logger = get_logger("tts_service")

class TTSService:
    """Service layer class orchestrating text-to-speech generation and playback."""
    
    def __init__(self, audio_service: AudioService = None):
        self.audio_service = audio_service or AudioService()
        
    def say(self, text: str) -> None:
        """
        Generates speech for the given text and plays it synchronously using the AudioService.
        
        Args:
            text: The text to speak.
        """
        try:
            # Generate the cached or new MP3 file path
            mp3_path = speak(text)
            
            # Delegate to AudioService for playback
            self.audio_service.play_file(mp3_path)
        except Exception as e:
            logger.error(f"Error in TTSService.say(): {e}")
