from pydantic import BaseModel
from src.models.wakeword import WakeState, WakePhrase

class WakeWordDetected(BaseModel):
    """Fired when a wake phrase is successfully detected."""
    phrase: WakePhrase

class SessionExpired(BaseModel):
    """Fired when an ActivationSession times out (Conversation Timeout)."""
    session_id: str

class StateChanged(BaseModel):
    """Fired when the assistant transitions through the WakeState machine."""
    old_state: WakeState
    new_state: WakeState
