from src.routing.classifier import IntentClassifier
from src.models.intent_result import RouterResult
from src.routing.intent import Intent
from src.utils.settings import ENABLE_INTENT_ROUTER, INTENT_LOW_CONFIDENCE
from src.utils.logger import get_logger

logger = get_logger("intent_router")

class IntentRouter:
    """
    Stateless traffic controller. 
    Receives text, queries the IntentClassifier, evaluates confidence bands, 
    and assigns a Destination service.
    """
    def __init__(self):
        self.classifier = IntentClassifier()
        
    def route(self, normalized_text: str) -> RouterResult:
        if not ENABLE_INTENT_ROUTER:
            return RouterResult(
                intent=Intent.AUTOMATION,
                confidence=1.0,
                normalized_text=normalized_text,
                destination="Planner"
            )
            
        intent_result = self.classifier.classify(normalized_text)
        
        destination = "FallbackService"
        
        # Confidence Thresholding
        if intent_result.confidence < INTENT_LOW_CONFIDENCE:
            destination = "FallbackService"
        elif intent_result.intent == Intent.MIXED:
            destination = "FallbackService"
        elif intent_result.intent == Intent.UNKNOWN:
            destination = "FallbackService"
        elif intent_result.intent == Intent.AUTOMATION:
            destination = "Planner"
        elif intent_result.intent == Intent.LLM_CHAT:
            destination = "LLMChatService"
        elif intent_result.intent == Intent.CONVERSATION:
            destination = "ConversationService"
        else:
            # Catch-all for future intents (VISION, BROWSER, etc) not yet implemented
            destination = "FallbackService"
            
        return RouterResult(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            normalized_text=normalized_text,
            destination=destination
        )
