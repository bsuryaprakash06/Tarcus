import json
import os
from typing import Dict
from src.utils.logger import get_logger
from src.utils import settings
from src.models.normalization import NormalizationResult, NormalizationChange, NormalizationCategory
from src.normalization.dictionaries import APPLICATIONS, BRANDS, TECHNICAL_TERMS, OS_COMMANDS
from src.normalization.aliases import ALIASES
from src.normalization.rules import apply_dictionary_rules, normalize_whitespace

logger = get_logger("normalization")

class SpeechNormalizer:
    """
    Deterministic rule-based normalization engine. 
    Improves transcription accuracy before intent routing.
    Does NOT guess semantics.
    """
    def __init__(self):
        self.user_dictionary = self._load_user_dictionary()
        
    def _load_user_dictionary(self) -> Dict[str, str]:
        path = "config/user_dictionary.json"
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load user dictionary: {e}")
        return {}

    def normalize(self, text: str) -> NormalizationResult:
        if not settings.ENABLE_SPEECH_NORMALIZATION:
            return NormalizationResult(
                original_text=text,
                normalized_text=text,
                confidence=1.0,
                changes=[]
            )

        original_text = text
        current_text = text
        all_changes = []
        
        # 1. User Defined (Highest Priority)
        if self.user_dictionary:
            current_text, changes = apply_dictionary_rules(current_text, self.user_dictionary, NormalizationCategory.USER_DEFINED)
            all_changes.extend(changes)
            
        # 2. OS Commands
        if getattr(settings, "ENABLE_OS_NORMALIZATION", True):
            current_text, changes = apply_dictionary_rules(current_text, OS_COMMANDS, NormalizationCategory.OS_COMMAND)
            all_changes.extend(changes)
            
        # 3. Applications
        current_text, changes = apply_dictionary_rules(current_text, APPLICATIONS, NormalizationCategory.APPLICATION)
        all_changes.extend(changes)
            
        # 4. Brands
        if getattr(settings, "ENABLE_BRAND_NORMALIZATION", True):
            current_text, changes = apply_dictionary_rules(current_text, BRANDS, NormalizationCategory.BRAND)
            all_changes.extend(changes)
            
        # 5. Technical Terms
        if getattr(settings, "ENABLE_TECHNICAL_NORMALIZATION", True):
            current_text, changes = apply_dictionary_rules(current_text, TECHNICAL_TERMS, NormalizationCategory.TECHNICAL_TERM)
            all_changes.extend(changes)
            
        # 6. Aliases
        if getattr(settings, "ENABLE_ALIAS_EXPANSION", True):
            current_text, changes = apply_dictionary_rules(current_text, ALIASES, NormalizationCategory.ALIAS)
            all_changes.extend(changes)
            
        # 7. Whitespace cleanup
        normalized_text = normalize_whitespace(current_text)
            
        # Calculate deterministic confidence
        # Since these are highly rigid word-boundary regex matches, we are extremely confident (0.98) if rules apply.
        confidence = 0.98 if all_changes else 1.0
        
        return NormalizationResult(
            original_text=original_text,
            normalized_text=normalized_text,
            confidence=confidence,
            changes=all_changes
        )
