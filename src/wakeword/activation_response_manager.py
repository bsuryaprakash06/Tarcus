import random
import os
from src.models.wakeword import WakeResponseMode
from src.utils.settings import SOUNDS_DIR, WAKE_RESPONSE_MODE
from src.utils.logger import get_logger

logger = get_logger("wakeword.response_manager")

class ActivationResponseManager:
    """
    Handles acknowledging the user when the assistant wakes up.
    """
    def __init__(self, tts_service=None):
        self.tts_service = tts_service
        self.mode = WakeResponseMode(WAKE_RESPONSE_MODE.upper())
        self.responses = [
            "Yes?",
            "I'm listening.",
            "Ready.",
            "Go ahead.",
            "What can I do?"
        ]

    def acknowledge(self):
        if self.mode == WakeResponseMode.SILENT:
            logger.debug("Wake response: SILENT mode.")
            return

        elif self.mode == WakeResponseMode.CHIME:
            logger.debug("Wake response: CHIME mode.")
            self._play_chime()

        elif self.mode == WakeResponseMode.VOICE:
            phrase = random.choice(self.responses)
            logger.debug(f"Wake response: VOICE mode. Saying '{phrase}'")
            if self.tts_service:
                self.tts_service.speak(phrase, block=False)
            else:
                logger.warning("TTS Service not provided to ActivationResponseManager.")

    def _play_chime(self):
        # We can use PyAudio, sounddevice, or playsound to play the chime.
        # For simplicity, if we have a chime file, we play it.
        chime_path = SOUNDS_DIR / "ding.wav"
        if not chime_path.exists():
            logger.warning(f"Chime file not found at {chime_path}. Cannot play chime.")
            return
            
        try:
            # We use a simple cross-platform sound player if available, or just sounddevice
            # To avoid blocking, we could load it and play it async.
            import soundfile as sf
            import sounddevice as sd
            data, fs = sf.read(str(chime_path))
            sd.play(data, fs) # Non-blocking by default
        except Exception as e:
            logger.error(f"Failed to play chime: {e}")
