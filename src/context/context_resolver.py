import re
from typing import Tuple, List
from src.utils.logger import get_logger

logger = get_logger("context.resolver")

class ContextResolver:
    """Resolves ambiguous pronouns against explicitly typed memory buckets."""
    
    PRONOUNS = {"it", "them", "that", "this"}
    
    def __init__(self, context_service):
        self.context_service = context_service
        
    def resolve_reference(self, text: str, intent: str) -> Tuple[str, float]:
        """
        Replaces pronouns in text using the correct semantic scope bucket.
        Returns the resolved text and a confidence score.
        """
        # Extract only words, stripping punctuation
        words = re.findall(r'\b\w+\b', text.lower())
        has_pronoun = any(p in words for p in self.PRONOUNS)
        
        if not has_pronoun:
            return text, 1.0
            
        resolved_entity = None
        confidence = 1.0
        
        if intent == "AUTOMATION":
            resolved_entity, confidence = self._resolve_automation()
        elif intent == "KNOWLEDGE":
            resolved_entity, confidence = self._resolve_knowledge()
        elif intent == "CONVERSATION":
            return text, 1.0
            
        if not resolved_entity:
            # We don't know what it is (or it's ambiguous)
            return text, confidence if confidence < 1.0 else 0.40
            
        if confidence < 0.60:
            # Found multiple conflicting things on stack, needs clarification
            return text, confidence
            
        # Replace the first occurrence (simplified replacement logic)
        for p in self.PRONOUNS:
            if re.search(r'\b' + p + r'\b', text.lower()):
                text = re.sub(r'\b' + p + r'\b', resolved_entity, text, count=1, flags=re.IGNORECASE)
                break
                
        logger.info(f"Resolved reference to '{resolved_entity}' (Scope: {intent})")
        return text, confidence

    def _resolve_automation(self) -> Tuple[str, float]:
        """
        Priority:
        1. Entity Stack (Most Recent)
        """
        ac = self.context_service.automation_context
        
        all_entities = ac.applications + ac.files + ac.folders + ac.websites
        all_entities.sort(key=lambda x: x.last_accessed, reverse=True)
        
        if not all_entities:
            return None, 1.0
            
        most_recent = all_entities[0]
        
        # If the top two entities share a very close access time (e.g. executed in same workflow)
        if len(all_entities) > 1:
            second_recent = all_entities[1]
            if abs(most_recent.last_accessed - second_recent.last_accessed) < 3.0: 
                # Highly Ambiguous (e.g. "Open Notepad and Calculator. Close it.")
                logger.warning(f"Ambiguous automation reference: {most_recent.name} vs {second_recent.name}")
                return None, 0.50
                
        return most_recent.name, 1.0
        
    def _resolve_knowledge(self) -> Tuple[str, float]:
        kc = self.context_service.knowledge_context
        if kc.current_topic:
            return kc.current_topic, 1.0
        elif kc.previous_topic:
            return kc.previous_topic, 0.8
        return None, 1.0
