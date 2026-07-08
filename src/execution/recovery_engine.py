from src.models.target import TargetSession, TargetState
from src.automation.driver import AutomationBackend
from src.automation.interaction_manager import InteractionManager
from src.utils.logger import get_logger
from src.events.pipeline_events import PipelineEventBus

logger = get_logger("execution.recovery_engine")

import warnings
from typing import Any
from src.utils.logger import get_logger
from pydantic import BaseModel

logger = get_logger("execution.recovery_engine")

class RecoveredEvent(BaseModel):
    """Deprecated: Use src.verification.verification_events.RecoverySucceeded instead."""
    target_id: str
    strategy: str

class RecoveryEngine:
    """
    DEPRECATED: Use src.verification.recovery_engine.RecoveryEngine instead.
    This class is maintained only as a thin wrapper to prevent breaking legacy imports.
    """
    def __init__(self, backend: Any, manager: Any):
        warnings.warn(
            "src.execution.recovery_engine.RecoveryEngine is deprecated. "
            "Use src.verification.recovery_engine.RecoveryEngine instead.",
            DeprecationWarning, stacklevel=2
        )
        logger.warning("Instantiated deprecated RecoveryEngine.")
        self.backend = backend
        self.manager = manager
        
    def recover_focus(self, session: Any) -> bool:
        # Return False to let the new pipeline handle things if invoked by legacy code
        return False
