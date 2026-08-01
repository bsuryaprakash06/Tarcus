from enum import Enum

class AudioState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    RECORDING = "RECORDING"
    TRANSCRIBING = "TRANSCRIBING"
    PLAYING = "PLAYING"
    INTERRUPTED = "INTERRUPTED"
