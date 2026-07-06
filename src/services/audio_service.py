import ctypes
import os
import time
from pathlib import Path
from queue import Queue
from src.utils.logger import get_logger
from src.utils.exceptions import AudioPlaybackError

logger = get_logger("audio_service")

class AudioService:
    """Service layer class responsible for audio file playback and queue orchestration using Windows native MCI API."""
    
    def __init__(self):
        self._queue = Queue()
        self._is_playing = False

    def play_file(self, file_path: Path) -> None:
        """
        Plays an audio file synchronously using Windows Media Control Interface (MCI).
        
        Args:
            file_path: Path to the audio file.
            
        Raises:
            AudioPlaybackError: If playback fails.
        """
        if not file_path.exists():
            logger.error(f"Audio file not found: {file_path}")
            raise AudioPlaybackError(f"Audio file does not exist: {file_path}")

        abs_path = str(file_path.resolve())
        logger.info(f"Playing audio file: {abs_path}")
        
        try:
            self._is_playing = True
            alias = f"audio_play_{os.getpid()}"
            
            # Open media file
            open_command = f'open "{abs_path}" type mpegvideo alias {alias}'
            ret = ctypes.windll.winmm.mciSendStringW(open_command, None, 0, 0)
            if ret != 0:
                raise AudioPlaybackError(f"MCI open command failed with code {ret}")
                
            try:
                # Play asynchronously so Python thread remains unblocked
                play_command = f'play {alias}'
                ret = ctypes.windll.winmm.mciSendStringW(play_command, None, 0, 0)
                if ret != 0:
                    raise AudioPlaybackError(f"MCI play command failed with code {ret}")
                    
                # Poll the MCI device status to know when playback is finished
                status_buffer = ctypes.create_unicode_buffer(256)
                while self._is_playing:
                    ctypes.windll.winmm.mciSendStringW(f'status {alias} mode', status_buffer, 255, 0)
                    if status_buffer.value == "stopped":
                        break
                    time.sleep(0.05) # Check 20 times a second for instant cancellation response
            finally:
                # Always close the device to release system resources
                close_command = f'close {alias}'
                ctypes.windll.winmm.mciSendStringW(close_command, None, 0, 0)
                self._is_playing = False
                
            logger.info("Audio playback completed successfully.")
        except Exception as e:
            self._is_playing = False
            logger.error(f"Failed to play audio file via MCI: {e}")
            raise AudioPlaybackError(f"Audio playback error: {e}") from e

    def enqueue(self, file_path: Path) -> None:
        """
        Adds an audio file to the playback queue.
        (For future async queuing architecture).
        """
        logger.info(f"Enqueued audio file: {file_path}")
        self._queue.put(file_path)

    def stop(self) -> None:
        """
        Stops any ongoing playback.
        (For future async interruption architecture).
        """
        logger.info("Requested audio playback stop.")
        alias = f"audio_play_{os.getpid()}"
        ctypes.windll.winmm.mciSendStringW(f'stop {alias}', None, 0, 0)
        self._is_playing = False
