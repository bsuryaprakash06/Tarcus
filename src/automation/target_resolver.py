from typing import Optional
from rapidfuzz import fuzz
from src.automation.target_registry import TargetRegistry
from src.models.target import Target
from src.utils.logger import get_logger

logger = get_logger("automation.target_resolver")

class TargetResolver:
    """
    Resolves natural language references to a specific Target in the Registry.
    """
    def __init__(self):
        self.registry = TargetRegistry()
        
    def resolve(self, reference: str, min_score: float = 60.0) -> Optional[Target]:
        """
        Finds the best matching Target based on name using RapidFuzz.
        """
        targets = self.registry.list_targets(active_only=True)
        if not targets:
            return None
            
        best_match = None
        best_score = 0.0
        
        for t in targets:
            score = fuzz.partial_ratio(reference.lower(), t.name.lower())
            if score > best_score:
                best_score = score
                best_match = t
                
        if best_match and best_score >= min_score:
            logger.info(f"Resolved '{reference}' -> {best_match.id} ({best_match.name}) with score {best_score}")
            return best_match
            
        logger.warning(f"Failed to resolve target for '{reference}'. Best score: {best_score}")
        return None
