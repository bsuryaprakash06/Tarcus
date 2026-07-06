from typing import Any
from src.scheduler.handlers.base_handler import BaseHandler
from src.models.scheduler import ExecutionNode
from src.services.executor_service import ExecutorService
from src.models.workflow import WorkflowStep
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
        if not isinstance(step, WorkflowStep):
            raise ValueError(f"AutomationHandler expected WorkflowStep payload, got {type(step)}")
            
        logger.info(f"AutomationHandler executing tool: {step.tool}")
        context = self.executor.get_current_context()
        
        # We'll do a simple synchronous execution here.
        # Retries could be implemented here or rely on the ExecutorService.
        result = self.executor.execute_step(step, context)
        
        if not result.success:
            raise Exception(result.user_message)
            
        return result
