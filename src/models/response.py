from enum import Enum
from pydantic import BaseModel

class ResponseMode(str, Enum):
    """Categorizes the high-level intent of the voice response."""
    AUTOMATION = "AUTOMATION"
    KNOWLEDGE = "KNOWLEDGE"
    CONVERSATION = "CONVERSATION"
    ERROR = "ERROR"
    CONFIRMATION = "CONFIRMATION"
    WARNING = "WARNING"

class ResponseProfile(BaseModel):
    """
    Defines presentation, styling, and length constraints.
    Passed to the LLM to govern generation natively.
    """
    mode: ResponseMode
    max_sentences: int = 1
    ask_followup: bool = False
    style: str = "concise"
    verbosity: str = "short"

class FormattedResponse(BaseModel):
    """
    The final processed payload handed to the Text-to-Speech engine.
    """
    raw_text: str
    formatted_text: str
    ssml: str
    estimated_duration: float
