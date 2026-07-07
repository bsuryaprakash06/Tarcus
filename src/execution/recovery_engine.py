from src.models.target import TargetSession, TargetState
from src.automation.driver import AutomationBackend
from src.automation.interaction_manager import InteractionManager
from src.utils.logger import get_logger
from src.events.pipeline_events import PipelineEventBus

logger = get_logger("execution.recovery_engine")

from pydantic import BaseModel

class RecoveredEvent(BaseModel):
    target_id: str
    strategy: str

class RecoveryEngine:
    """
    Handles self-healing for interactions (e.g., restoring minimized windows, refocusing).
    """
    def __init__(self, backend: AutomationBackend, manager: InteractionManager):
        self.backend = backend
        self.manager = manager
        self.event_bus = PipelineEventBus()
        
    def recover_focus(self, session: TargetSession) -> bool:
        """Attempts to restore and refocus the target."""
        logger.info(f"Attempting to recover focus for target {session.target.id} ({session.target.friendly_name})")
        
        # Try generic backend focus which usually handles restore
        if self.backend.focus(session):
            self.manager.update_state(session.target.id, TargetState.ACTIVE)
            self.event_bus.publish_event(RecoveredEvent(target_id=session.target.id, strategy="backend_focus"))
            logger.info("Recovery successful.")
            return True
            
        logger.warning("Recovery failed.")
        return False
