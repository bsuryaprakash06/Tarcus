import warnings
from typing import Optional, Any
from src.utils.logger import get_logger

logger = get_logger("automation.target_resolver")

class TargetResolver:
    """
    DEPRECATED: Use src.interaction.semantic_resolver.SemanticResolver instead.
    """
    def __init__(self):
        warnings.warn(
            "src.automation.target_resolver.TargetResolver is deprecated. "
            "Use src.interaction.semantic_resolver.SemanticResolver instead.",
            DeprecationWarning, stacklevel=2
        )
        
    def resolve_primary_edit(self, base_target_id: str) -> Optional[Any]:
        return None
