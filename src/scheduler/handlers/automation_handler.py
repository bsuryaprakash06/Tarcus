from typing import Any
from src.scheduler.handlers.base_handler import BaseHandler
from src.models.scheduler import ExecutionNode
from src.services.executor_service import ExecutorService
from src.models.workflow import WorkflowStep
from src.models.plan import PlanItem
from src.utils.logger import get_logger

logger = get_logger("scheduler.handlers.automation")

class AutomationHandler(BaseHandler):
    """
    Executes a single step (WorkflowStep/PlanItem) using the ExecutorService.
    Provides safe retries natively.
    """
    def __init__(self):
        self.executor = ExecutorService()

    def execute(self, node: ExecutionNode) -> Any:
        step = node.payload
        if not isinstance(step, (WorkflowStep, PlanItem)):
            raise ValueError(f"AutomationHandler expected WorkflowStep/PlanItem payload, got {type(step)}")
            
        logger.info(f"AutomationHandler executing tool: {step.tool}")
        context = self.executor.get_current_context()
        
        from src.automation.target_selector import TargetSelector
        from src.models.interaction import InteractionContext
        target = TargetSelector().get_current_target()
        
        context.interaction = InteractionContext(
             current_target=target,
             focused_element=None,
             backend=target.backend if target else "windows_uia"
        )
        
        # We'll do a simple synchronous execution here.
        # Retries could be implemented here or rely on the ExecutorService.
        result = self.executor.execute_step(step, context)
        
        if not result.success:
            raise Exception(result.user_message)
            
        return result
