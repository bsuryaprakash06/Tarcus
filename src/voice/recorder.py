from datetime import datetime
from pathlib import Path
import sounddevice as sd
from scipy.io import wavfile
from src.utils.settings import RECORDINGS_DIR, SAMPLE_RATE, CHANNELS
from src.utils.logger import get_logger
from src.utils.exceptions import RecordingError

logger = get_logger("recorder")

def record_audio(duration: int = 5) -> Path:
    """
    Records audio from the microphone for the specified duration
    and saves it to a timestamped WAV file in the recordings directory.
    
    Args:
        duration: The duration of the recording in seconds.
        
    Returns:
        Path: The file path where the recording is saved.
        
    Raises:
        RecordingError: If recording or saving the file fails.
    """
    try:
        logger.info(f"Starting recording for {duration} seconds...")
        
        # sd.rec records audio from default input device
        recording = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16"
        )
        sd.wait()  # Block until the recording is finished
        logger.info("Recording finished.")
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = RECORDINGS_DIR / f"{timestamp}.wav"
        
        # Ensure the parent directories exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the audio file
        wavfile.write(output_path, SAMPLE_RATE, recording)
        logger.info(f"Saved recording to {output_path}")
        
        return output_path
    except Exception as e:
        logger.error(f"Error during audio recording: {str(e)}")
        raise RecordingError(f"Failed to record audio: {str(e)}") from e
