import asyncio
import hashlib
from pathlib import Path
import edge_tts
from src.utils.settings import VOICE_NAME, VOICE_RATE, VOICE_VOLUME, SOUNDS_DIR
from src.utils.logger import get_logger
from src.utils.exceptions import TTSError

logger = get_logger("text_to_speech")

async def _generate_speech_async(text: str, mp3_path: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE_NAME, rate=VOICE_RATE, volume=VOICE_VOLUME)
    await communicate.save(str(mp3_path))

def speak(text: str) -> Path:
    """
    Generates an audio file from text using Edge TTS and returns the path to the MP3.
    Caches the generated speech by voice configuration and text hash.
    
    Args:
        text: The text to speak.
        
    Returns:
        Path: The file path of the generated or cached MP3 audio.
        
    Raises:
        TTSError: If TTS generation fails.
    """
    if not text.strip():
        logger.warning("Empty text passed to speak(). Skipping generation.")
        raise TTSError("Cannot generate speech for empty text.")
        
    try:
        # Generate cache key incorporating voice settings to prevent reuse if settings change
        key_source = f"{VOICE_NAME}_{VOICE_RATE}_{VOICE_VOLUME}_{text.strip()}"
        text_hash = hashlib.md5(key_source.encode("utf-8")).hexdigest()
        output_mp3_path = SOUNDS_DIR / f"tts_{text_hash}.mp3"
        
        # Check cache
        if output_mp3_path.exists():
            logger.info(f"Using cached speech audio for text: '{text}'")
            return output_mp3_path
            
        logger.info(f"Generating new TTS for: '{text}'")
        
        # Ensure output directory exists
        output_mp3_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run async generation inside sync method
        asyncio.run(_generate_speech_async(text, output_mp3_path))
        
        logger.info(f"TTS generation complete. File saved to {output_mp3_path}")
        return output_mp3_path
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise TTSError(f"Failed to generate speech: {e}") from e
