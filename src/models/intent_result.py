from pydantic import BaseModel
from src.routing.intent import Intent

class IntentResult(BaseModel):
    """
    The raw classification result parsed directly from the LLM classifier.
    """
    intent: Intent
    confidence: float
    reason: str

class RouterResult(BaseModel):
    """
    The finalized routing decision wrapped with destination and text context.
    """
    intent: Intent
    confidence: float
    normalized_text: str
    destination: str
