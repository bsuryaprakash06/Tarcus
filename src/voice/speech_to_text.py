from pathlib import Path
import whisper
from src.utils.settings import WHISPER_MODEL_NAME, MODELS_DIR
from src.utils.logger import get_logger
from src.utils.exceptions import TranscriptionError
from src.models.transcription import TranscriptionResult

logger = get_logger("speech_to_text")

_model = None

def get_model():
    """
    Loads and caches the Whisper model instance.
    Downloads the model to the local models/ directory if not present.
    """
    global _model
    if _model is None:
        try:
            logger.info(f"Loading Whisper model '{WHISPER_MODEL_NAME}' (downloading if necessary)...")
            # download_root directs the cache directory to local models/ folder
            _model = whisper.load_model(WHISPER_MODEL_NAME, download_root=str(MODELS_DIR))
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise TranscriptionError(f"Could not initialize Whisper: {str(e)}") from e
    return _model

def transcribe(audio_path: Path) -> TranscriptionResult:
    """
    Transcribes the audio file using the preloaded Whisper model.
    
    Args:
        audio_path: The Path to the WAV audio file.
        
    Returns:
        TranscriptionResult: The typed transcription result.
        
    Raises:
        TranscriptionError: If transcription fails.
    """
    if not audio_path.exists():
        logger.error(f"Audio file not found: {audio_path}")
        raise TranscriptionError(f"Audio file does not exist: {audio_path}")
        
    try:
        model = get_model()
        logger.info(f"Transcribing audio file: {audio_path}")
        
        # Transcribe audio. fp16=False enforces CPU execution (prevents PyTorch warning)
        result = model.transcribe(str(audio_path), fp16=False)
        
        text = result.get("text", "").strip()
        language = result.get("language", "")
        
        # Calculate duration from segments
        duration = 0.0
        segments = result.get("segments", [])
        if segments:
            duration = segments[-1].get("end", 0.0)
            
        logger.info(f"Transcription completed. Text: '{text}' [Lang: {language}, Dur: {duration:.2f}s]")
        
        return TranscriptionResult(
            text=text,
            language=language,
            duration=duration
        )
    except Exception as e:
        logger.error(f"Error during audio transcription: {str(e)}")
        raise TranscriptionError(f"Failed to transcribe audio: {str(e)}") from e
