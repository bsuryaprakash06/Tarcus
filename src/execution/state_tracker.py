import copy
from typing import Dict, Any, List, Optional
from src.models.workflow_execution import ExecutionWorkflow, ExecutionStep, StateSnapshot, ExecutionState
from src.utils.logger import get_logger

logger = get_logger("execution.state_tracker")

class StateTracker:
    """Maintains execution history using StateSnapshots, enabling pause/resume and rollback."""
    
    def __init__(self, workflow: ExecutionWorkflow):
        self.workflow = workflow
        
    def get_current_step(self) -> Optional[ExecutionStep]:
        if self.workflow.current_step_index < len(self.workflow.steps):
            return self.workflow.steps[self.workflow.current_step_index]
        return None
        
    def advance_step(self) -> bool:
        """Moves to the next step. Returns True if advanced, False if workflow complete."""
        self.workflow.current_step_index += 1
        return self.workflow.current_step_index < len(self.workflow.steps)
        
    def capture_before_snapshot(self, step: ExecutionStep, context: Dict[str, Any]):
        if not step.snapshot:
            step.snapshot = StateSnapshot()
        # Deep copy to ensure history isn't mutated
        step.snapshot.before = copy.deepcopy(context)
        logger.debug(f"Captured 'before' snapshot for step {step.step_id}")
        
    def capture_after_snapshot(self, step: ExecutionStep, context: Dict[str, Any]):
        if not step.snapshot:
            step.snapshot = StateSnapshot()
        step.snapshot.after = copy.deepcopy(context)
        logger.debug(f"Captured 'after' snapshot for step {step.step_id}")
        
    def mark_workflow_status(self, status: ExecutionState):
        self.workflow.status = status
        logger.info(f"Workflow {self.workflow.workflow_id} status changed to {status.value}")
