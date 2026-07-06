from typing import List, Dict
from src.utils.logger import get_logger

logger = get_logger("response.merger")

class ResponseMerger:
    """Intelligently merges the text outputs of independent atomic tasks back together for TTS."""
    
    @staticmethod
    def merge(responses: List[Dict[str, str]]) -> str:
        """
        Takes a list of dicts: {"intent": "CONVERSATION", "text": "Hello there."}
        Returns a naturally flowing cohesive response (Conversation -> Knowledge -> Automation).
        """
        conversation_parts = []
        knowledge_parts = []
        automation_parts = []
        fallback_parts = []
        
        for resp in responses:
            intent = resp.get("intent", "UNKNOWN")
            text = resp.get("text", "")
            if not text:
                continue
                
            if intent == "CONVERSATION":
                conversation_parts.append(text)
            elif intent == "KNOWLEDGE":
                knowledge_parts.append(text)
            elif intent == "AUTOMATION":
                automation_parts.append(text)
            else:
                fallback_parts.append(text)
                
        merged = []
        
        # 1. Greetings / conversational filler first
        if conversation_parts:
            merged.append(" ".join(conversation_parts))
            
        # 2. Heavy educational content second
        if knowledge_parts:
            merged.append(" ".join(knowledge_parts))
            
        # 3. Execution confirmations last (so the user knows it finished)
        if automation_parts:
            merged.append(" ".join(automation_parts))
            
        if fallback_parts:
            merged.append(" ".join(fallback_parts))
            
        final_text = " ".join(merged).strip()
        logger.info(f"Merged {len(responses)} diverse responses into: '{final_text}'")
        return final_text
