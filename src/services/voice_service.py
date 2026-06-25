import time
from rich.console import Console
from src.utils.logger import get_logger
from src.voice.recorder import record_audio
from src.voice.speech_to_text import transcribe
from src.models.transcription import TranscriptionResult

logger = get_logger("voice_service")
console = Console()

class VoiceService:
    """Service layer class orchestrating voice-related pipelines."""
    
    def __init__(self):
        pass

    def listen(self, duration: int = 5) -> TranscriptionResult:
        """
        Orchestrates recording and transcribing voice input, recording elapsed times.
        
        Args:
            duration: Recording duration in seconds.
            
        Returns:
            TranscriptionResult: The typed transcription result.
        """
        total_start = time.time()
        
        # 1. Record audio
        rec_start = time.time()
        audio_path = record_audio(duration)
        rec_duration = time.time() - rec_start
        logger.info(f"Recording: {rec_duration:.2f} s")
        
        # Print feedback to user console before starting CPU-heavy transcription
        console.print("[bold yellow]⚙️ Processing...[/bold yellow]")
        
        # 2. Transcribe audio
        transcribe_start = time.time()
        result = transcribe(audio_path)
        transcribe_duration = time.time() - transcribe_start
        logger.info(f"Transcription: {transcribe_duration:.2f} s")
        
        total_duration = time.time() - total_start
        logger.info(f"Total: {total_duration:.2f} s")
        
        return result
