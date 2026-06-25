from enum import Enum

class AssistantStatus(Enum):
    """Represents the operational status of the Voice Assistant."""
    IDLE = "IDLE"
    RECORDING = "RECORDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
