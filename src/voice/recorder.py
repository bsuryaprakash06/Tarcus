import time
from datetime import datetime
from pathlib import Path
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from src.utils.settings import RECORDINGS_DIR, SAMPLE_RATE, CHANNELS
from src.utils.logger import get_logger
from src.utils.exceptions import RecordingError
from src.voice.voice_activity_detector import VoiceActivityDetector

logger = get_logger("recorder")

def record_audio(duration: int = 5) -> Path:
    """
    Records audio from the microphone dynamically using VAD, falling back to 
    a maximum duration if VAD is disabled.
    Saves it to a timestamped WAV file in the recordings directory.
    
    Args:
        duration: Kept for backward compatibility, but overridden by VAD settings.
        
    Returns:
        Path: The file path where the recording is saved.
        
    Raises:
        RecordingError: If recording or saving the file fails.
    """
    try:
        vad = VoiceActivityDetector()
        audio_frames = []

        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio stream status: {status}")
            
            # Copy the frame data because indata memory is reused
            audio_frames.append(indata.copy())
            vad.process_frame(indata)

        logger.info("Starting audio stream recording...")
        
        # Start the InputStream
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=audio_callback
        ):
            # Block the main thread while the VAD determines we should continue
            while vad.should_continue():
                time.sleep(0.1)

        logger.info("Recording finished.")
        
        if not audio_frames:
            raise RecordingError("No audio frames were captured.")
            
        # Concatenate all frames into a single numpy array
        recording = np.concatenate(audio_frames, axis=0)

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
