import warnings
from typing import Optional, Any
from src.utils.logger import get_logger

logger = get_logger("automation.target_registry")

class TargetRegistry:
    """
    DEPRECATED: Use src.interaction.interaction_graph.InteractionGraph instead.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TargetRegistry, cls).__new__(cls)
            warnings.warn(
                "src.automation.target_registry.TargetRegistry is deprecated. "
                "Use src.interaction.interaction_graph.InteractionGraph instead.",
                DeprecationWarning, stacklevel=2
            )
        return cls._instance

    def register_target(self, target_def: Any) -> Any:
        return target_def

    def update_lifecycle(self, target_id: str, new_state: Any):
        pass

    def get_target(self, target_id: str) -> Optional[Any]:
        return None

    def list_targets(self, active_only: bool = True) -> list:
        return []
