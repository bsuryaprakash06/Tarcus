import re
from src.utils.logger import get_logger

logger = get_logger("conversation_service")

# A mapping of simple Regex patterns to instant responses to save API latency
CACHED_RESPONSES = {
    r"\b(hi|hello|hey|greetings)\b": "Hello! How can I help you?",
    r"\b(good morning)\b": "Good morning!",
    r"\b(good night|bye|goodbye)\b": "Goodbye! Let me know if you need anything else.",
    r"\b(thanks|thank you)\b": "You're very welcome!",
    r"\b(how are you)\b": "I'm functioning perfectly, thank you for asking!",
}

class ConversationService:
    """
    Handles simple pleasantries locally to bypass the LLM entirely, minimizing latency.
    """
    def respond(self, text: str, history_str: str = "") -> str:
        text_lower = text.lower()
        
        # Check local cache first
        for pattern, response in CACHED_RESPONSES.items():
            if re.search(pattern, text_lower):
                logger.debug(f"Conversation cache hit for pattern: {pattern}")
                return response
                
        # Generic conversational fallback if categorized as conversation but misses cache
        return "I am here. What would you like to do?"
