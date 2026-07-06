import re
from src.utils.logger import get_logger
from src.providers import get_provider_from_settings

logger = get_logger("dialogue.merge")

class HybridMergeEngine:
    """Intelligently merges a user's clarification reply into a suspended original request."""
    
    def __init__(self):
        self.provider = get_provider_from_settings()
        self.PRONOUNS = {"it", "them", "that", "this", "the first one", "the second one"}
        
    def merge(self, original_text: str, reply_text: str) -> str:
        """
        Attempts a fast deterministic regex merge. 
        Falls back to LLM for complex conversational replies.
        """
        # Try deterministic merge
        merged = self._deterministic_merge(original_text, reply_text)
        if merged:
            logger.info(f"Deterministic Merge: '{original_text}' + '{reply_text}' -> '{merged}'")
            return merged
            
        # Fallback to LLM merge
        merged = self._llm_merge(original_text, reply_text)
        logger.info(f"LLM Merge: '{original_text}' + '{reply_text}' -> '{merged}'")
        return merged

    def _deterministic_merge(self, original_text: str, reply_text: str) -> str:
        """Simple substitution if the reply is short and direct."""
        words = re.findall(r'\b\w+\b', reply_text.lower())
        
        # If the reply is too long, it's likely conversational ("Actually I meant the second one")
        if len(words) > 3:
            return None
            
        # If it contains conversational pivots, defer to LLM
        complex_markers = {"actually", "meant", "no", "yes", "nevermind", "forget"}
        if any(w in complex_markers for w in words):
            return None
            
        # Perform simple pronoun substitution
        for p in self.PRONOUNS:
            if re.search(r'\b' + p + r'\b', original_text.lower()):
                # Strip trailing punctuation from reply to avoid "Close Notepad.."
                clean_reply = reply_text.strip('.!?')
                return re.sub(r'\b' + p + r'\b', clean_reply, original_text, count=1, flags=re.IGNORECASE)
                
        return None
        
    def _llm_merge(self, original_text: str, reply_text: str) -> str:
        """Uses the LLM provider to syntactically synthesize complex answers."""
        system_prompt = (
            "You are a Dialogue Merge Engine. "
            "You will be given an 'Original Request' that was ambiguous, and a 'User Reply' providing clarification.\n"
            "Your job is to synthesize the final, unambiguous request in a single short sentence.\n"
            "Output ONLY the final merged string. Do not explain. Do not wrap in quotes."
        )
        user_prompt = f"Original Request: {original_text}\nUser Reply: {reply_text}"
        
        try:
            response = self.provider.generate(system_prompt=system_prompt, user_prompt=user_prompt)
            return response.text.strip().strip('"')
        except Exception as e:
            logger.error(f"LLM Merge failed: {e}")
            return f"{original_text} {reply_text}"
