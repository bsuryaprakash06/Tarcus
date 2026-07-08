import warnings
from typing import Any
from src.utils.logger import get_logger

logger = get_logger("automation.interaction_manager")

class InteractionManager:
    """
    DEPRECATED: Use src.interaction.interaction_manager.InteractionManager instead.
    This class is maintained only as a thin wrapper to prevent breaking legacy imports.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InteractionManager, cls).__new__(cls)
            warnings.warn(
                "src.automation.interaction_manager.InteractionManager is deprecated. "
                "Use src.interaction.interaction_manager.InteractionManager instead.",
                DeprecationWarning, stacklevel=2
            )
            logger.warning("Instantiated deprecated InteractionManager.")
        return cls._instance
        
    def discover_and_sync(self, backend: Any):
        pass
        
    def list_sessions(self, active_only: bool = True) -> list:
        return []

