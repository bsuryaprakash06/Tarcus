from src.scheduler.handlers.base_handler import BaseHandler
from src.models.scheduler import ExecutionNode
from src.models.workflow_execution import ExecutionWorkflow
from src.execution.execution_controller import ExecutionController
from src.utils.logger import get_logger

logger = get_logger("scheduler.handlers.workflow")

class WorkflowHandler(BaseHandler):
    """
    Executes a full ExecutionWorkflow by delegating to the ExecutionController.
    This replaces the legacy AutomationHandler for UI automation intents.
    """
    def execute(self, node: ExecutionNode) -> str:
        if not isinstance(node.payload, ExecutionWorkflow):
            raise ValueError(f"WorkflowHandler expected ExecutionWorkflow payload, got {type(node.payload)}")
            
        workflow = node.payload
        logger.info(f"WorkflowHandler delegating workflow {workflow.workflow_id} to ExecutionController")
        
        controller = ExecutionController(workflow)
        success = controller.run()
        
        if success:
            return f"Workflow {workflow.goal} completed successfully."
        else:
            raise RuntimeError(f"Workflow {workflow.goal} failed.")
