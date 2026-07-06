from enum import Enum

class PipelineState(str, Enum):
    """Detailed state machine for the UI Status Bar and metrics."""
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    TRANSCRIBING = "TRANSCRIBING"
    NORMALIZING = "NORMALIZING"
    RESOLVING_CONTEXT = "RESOLVING_CONTEXT"
    ROUTING = "ROUTING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    FORMATTING = "FORMATTING"
    SPEAKING = "SPEAKING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
