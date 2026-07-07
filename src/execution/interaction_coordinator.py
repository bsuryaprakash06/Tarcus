from typing import Optional, Dict, Any
from src.automation.interaction_manager import InteractionManager
from src.automation.target_resolver import TargetResolver
from src.execution.interaction_planner import InteractionPlanner, InteractionPlan
from src.execution.recovery_engine import RecoveryEngine
from src.execution.action_executor import ActionExecutor
from src.automation.driver import AutomationBackend
from src.models.target import TargetSession, TargetState, VerificationResult
from src.utils.logger import get_logger

logger = get_logger("execution.interaction_coordinator")

class InteractionCoordinator:
    """
    The 'brain' of interaction. Coordinates resolution, planning, recovery, and execution.
    Called by the Execution Controller for all UI-related steps.
    """
    def __init__(self, backend: AutomationBackend, action_executor: ActionExecutor):
        self.backend = backend
        self.manager = InteractionManager()
        self.resolver = TargetResolver()
        self.recovery_engine = RecoveryEngine(backend, self.manager)
        self.action_executor = action_executor
        
    def coordinate_interaction(self, intent: str, base_target_id: str, **kwargs) -> bool:
        """
        Orchestrates the full lifecycle of an interaction.
        intent: e.g., 'typing', 'clicking'
        """
        logger.info(f"Coordinating interaction '{intent}' for base target {base_target_id}")
        
        # 1. Resolve the best specific target (e.g., finding the edit control)
        # In a real system, the capability analyzer would inform this.
        target = None
        if intent == 'typing':
            target = self.resolver.resolve_primary_edit(base_target_id)
        
        # Fallback to the base target if resolution didn't yield a specific child
        if not target:
            session = self.manager.get_session(base_target_id)
            if not session:
                logger.error(f"Failed to resolve target and base session {base_target_id} not found.")
                return False
        else:
            session = self.manager.get_session(target.id) or self.manager.register_target(target)
            
        # 2. Plan the interaction
        if intent == 'typing':
            plan = InteractionPlanner.plan_typing(session, kwargs.get("text", ""), kwargs.get("clear_first", False))
        elif intent == 'clicking':
            plan = InteractionPlanner.plan_click(session, kwargs.get("double", False), kwargs.get("right", False))
        else:
            logger.error(f"Unknown interaction intent: {intent}")
            return False
            
        # 3. Execute the micro-plan
        return self._execute_plan(session, plan, intent, kwargs)
        
    def _execute_plan(self, session: TargetSession, plan: InteractionPlan, intent: str, args: Dict[str, Any]) -> bool:
        for step in plan.steps:
            if step == "focus":
                if not self.backend.focus(session):
                    if not self.recovery_engine.recover_focus(session):
                        return False
            elif step == "insert":
                if not self.backend.type(session, args.get("text", ""), args.get("clear_first", False)):
                    return False
            elif step == "click":
                if not self.backend.click(session, args.get("double", False), args.get("right", False)):
                    return False
            elif step == "verify":
                # For now, a mock verification success
                session.verification_result = VerificationResult.SUCCESS
            elif step == "update_session":
                session.record_interaction(intent)
                self.manager.update_state(session.target.id, TargetState.ACTIVE)
        
        return True
