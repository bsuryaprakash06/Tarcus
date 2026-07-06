from typing import Optional
from src.models.plan import ExecutionPlan
from src.workflow.workflow_engine import WorkflowEngine
from src.workflow.cancellation_manager import CancellationManager
from src.utils.settings import ENABLE_WORKFLOW_ENGINE

class WorkflowService:
    """Facade for the Workflow Engine exposing execution, pause, and cancellation."""
    
    def __init__(self):
        self.engine = WorkflowEngine()
        self.cancellation_manager = CancellationManager()
        self.active_workflow_id: Optional[str] = None
        
    def execute(self, plan: ExecutionPlan) -> str:
        """Initializes and executes a new workflow from a plan."""
        if not ENABLE_WORKFLOW_ENGINE:
            return ""
            
        workflow = self.engine.initialize_workflow(plan)
        self.active_workflow_id = workflow.workflow_id
        self.engine.execute(workflow.workflow_id)
        return workflow.workflow_id
        
    def execute_workflow(self, workflow) -> str:
        """Executes a pre-composed workflow from the WorkflowComposer."""
        if not ENABLE_WORKFLOW_ENGINE:
            return ""
            
        self.active_workflow_id = workflow.workflow_id
        self.engine.state_manager.save(workflow)
        self.engine.execute(workflow.workflow_id)
        return workflow.workflow_id
        
    def pause(self) -> None:
        """Requests a pause on the currently active workflow."""
        if ENABLE_WORKFLOW_ENGINE and self.active_workflow_id:
            self.cancellation_manager.request_pause(self.active_workflow_id)
            
    def resume(self) -> None:
        """Resumes the active paused workflow."""
        if ENABLE_WORKFLOW_ENGINE and self.active_workflow_id:
            self.engine.execute(self.active_workflow_id)
            
    def cancel(self) -> None:
        """Cancels the currently active workflow."""
        if ENABLE_WORKFLOW_ENGINE and self.active_workflow_id:
            self.cancellation_manager.request_cancel(self.active_workflow_id)
