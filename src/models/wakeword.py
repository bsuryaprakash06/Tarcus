from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
import time
from src.utils.settings import CONVERSATION_TIMEOUT, RECORDING_TIMEOUT

class WakeState(str, Enum):
    PASSIVE = "PASSIVE"
    WAKE_DETECTED = "WAKE_DETECTED"
    ACKNOWLEDGING = "ACKNOWLEDGING"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    RESPONDING = "RESPONDING"
    FOLLOW_UP = "FOLLOW_UP"

class WakeResponseMode(str, Enum):
    VOICE = "VOICE"
    CHIME = "CHIME"
    SILENT = "SILENT"

class WakePhrase(BaseModel):
    phrase: str
    confidence: float
    timestamp: float = Field(default_factory=time.time)

class ActivationSession(BaseModel):
    """Tracks a single conversational interaction session."""
    id: str
    wake_phrase: WakePhrase
    activated_time: float = Field(default_factory=time.time)
    last_activity: float = Field(default_factory=time.time)
    conversation_count: int = 0
    is_active: bool = True
    
    def touch(self):
        """Updates the last_activity timestamp to extend the session."""
        self.last_activity = time.time()
        
    def check_timeouts(self) -> bool:
        """
        Returns True if the session has expired due to the CONVERSATION_TIMEOUT.
        Recording timeout is handled separately by the VAD.
        """
        if not self.is_active:
            return True
        if (time.time() - self.last_activity) > CONVERSATION_TIMEOUT:
            self.is_active = False
            return True
        return False
