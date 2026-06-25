import os
import shutil
import sounddevice as sd
from src.utils.logger import get_logger
from src.utils.settings import RECORDINGS_DIR

logger = get_logger("startup")

def run_startup_checks() -> bool:
    """
    Performs initial validation checks to ensure the application environment is set up.
    Returns True if all checks pass, otherwise logs the error and returns False.
    """
    logger.info("Running startup environment checks...")
    
    # 1. Check microphone availability
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if not input_devices:
            logger.error("No input audio devices (microphones) found. Please connect a microphone.")
            return False
        logger.info(f"Microphone check passed: found {len(input_devices)} input device(s).")
    except Exception as e:
        logger.error(f"Failed to query audio devices: {e}")
        return False

    # 2. Check FFmpeg installation
    if not shutil.which("ffmpeg"):
        logger.error("FFmpeg not found in system PATH. Whisper transcription requires FFmpeg to be installed.")
        return False
    logger.info("FFmpeg check passed: executable found.")

    # 3. Check recording directory is writable
    try:
        test_file = RECORDINGS_DIR / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        logger.info("Recording directory write check passed.")
    except Exception as e:
        logger.error(f"Recording directory is not writable: {e}")
        return False

    # 4. Check Whisper model
    try:
        logger.info("Initializing Whisper model (this may take a moment)...")
        from src.voice.speech_to_text import get_model
        get_model()
        logger.info("Whisper model check passed.")
    except Exception as e:
        logger.error(f"Whisper model check failed: {e}")
        return False

    logger.info("All startup checks passed successfully.")
    return True
