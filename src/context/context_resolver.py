import re
import json
from typing import Tuple
from src.models.context import SessionContext
from src.providers import get_provider_from_settings
from src.utils.logger import get_logger

logger = get_logger("context.resolver")

class ContextResolver:
    """
    Implements a Hybrid (Deterministic -> LLM Fallback) reference resolution engine.
    """
    
    def __init__(self):
        self.provider = get_provider_from_settings()
        # Common pronouns that strongly suggest the need for reference resolution
        self.reference_triggers = re.compile(
            r'\b(it|this|that|them|those|the folder|that folder|the file|that file|the app|that app)\b', 
            re.IGNORECASE
        )

    def resolve(self, text: str, context: SessionContext) -> Tuple[str, float]:
        """
        Attempts to resolve references in the text.
        Returns the resolved text and a confidence score (0.0 to 1.0).
        """
        # 1. If no pronouns/references are found, skip resolution (Confidence 1.0)
        if not self.reference_triggers.search(text):
            return text, 1.0
            
        # 2. Stage 1: Deterministic Fast-Path
        fast_path_text, confidence = self._attempt_deterministic_resolution(text, context)
        if confidence >= 0.90:
            logger.debug(f"Deterministic resolution succeeded: '{text}' -> '{fast_path_text}' (Conf: {confidence})")
            return fast_path_text, confidence
            
        # 3. Stage 2: LLM Fallback
        logger.debug(f"Deterministic resolution failed/low confidence. Falling back to LLM for: '{text}'")
        return self._attempt_llm_resolution(text, context)
        
    def _attempt_deterministic_resolution(self, text: str, context: SessionContext) -> Tuple[str, float]:
        """Simple Regex replacements for unambiguous, single-entity contexts (Zero API latency)."""
        lower_text = text.lower()
        
        # 1. Folder references
        if "folder" in lower_text:
            if context.automation.last_folder:
                resolved = re.sub(r'\b(that folder|the folder|it)\b', context.automation.last_folder.value, text, flags=re.IGNORECASE)
                return resolved, 0.95
                
        # 2. File references
        if "file" in lower_text:
            if context.automation.last_file:
                resolved = re.sub(r'\b(that file|the file|it)\b', context.automation.last_file.value, text, flags=re.IGNORECASE)
                return resolved, 0.95
                
        # 3. Application references
        if "app" in lower_text or "application" in lower_text or "close it" in lower_text or "open it" in lower_text:
            if context.automation.last_application:
                resolved = re.sub(r'\b(it|that app|the app|the application)\b', context.automation.last_application.value, text, flags=re.IGNORECASE)
                return resolved, 0.95
                
        # If it's ambiguous or we don't have the explicit entity, we drop to the LLM (confidence 0)
        return text, 0.0
        
    def _attempt_llm_resolution(self, text: str, context: SessionContext) -> Tuple[str, float]:
        """Uses the LLM to intelligently rewrite the sentence based on all active context."""
        
        system_prompt = (
            "You are an intelligent linguistic context resolver. "
            "Your ONLY job is to replace pronouns ('it', 'that', 'them', etc.) in the user's sentence "
            "with the actual subject from the provided conversation context. "
            "Output your answer in JSON format containing 'resolved_text' and 'confidence' (float 0.0 to 1.0).\n\n"
            "CONTEXT:\n"
        )
        
        if context.automation.last_application:
            system_prompt += f"- Last App: {context.automation.last_application.value}\n"
        if context.automation.last_folder:
            system_prompt += f"- Last Folder: {context.automation.last_folder.value}\n"
        if context.knowledge.current_topic:
            system_prompt += f"- Current Topic: {context.knowledge.current_topic.value}\n"
            
        system_prompt += "\nRULES:\n"
        system_prompt += "1. If you can confidently determine what 'it' refers to, replace it.\n"
        system_prompt += "2. If there are multiple possible subjects and it is ambiguous, return the original text with low confidence (e.g. 0.4).\n"
        system_prompt += "3. If no pronoun needs replacing, return the original text with high confidence (1.0).\n"
        
        try:
            response = self.provider.generate(system_prompt=system_prompt, user_prompt=text, require_json=True)
            
            try:
                data = json.loads(response.text)
                resolved = data.get("resolved_text", text)
                confidence = float(data.get("confidence", 0.5))
                logger.debug(f"LLM resolution: '{text}' -> '{resolved}' (Conf: {confidence})")
                return resolved, confidence
            except json.JSONDecodeError:
                logger.warning(f"LLM returned invalid JSON for context resolution. Raw: {response.text}")
                return text, 0.0
                
        except Exception as e:
            logger.error(f"LLM resolution request failed: {e}")
            return text, 0.0
