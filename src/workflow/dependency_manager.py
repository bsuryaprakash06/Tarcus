from src.models.workflow import Workflow, StepStatus

class DependencyManager:
    """Evaluates step preconditions and dependencies."""
    
    @staticmethod
    def can_execute(step_id: str, workflow: Workflow) -> bool:
        """Determines if a step is allowed to execute based on its dependencies."""
        step = next((s for s in workflow.steps if s.step_id == step_id), None)
        if not step:
            return False
            
        # Check dependencies
        for dep_id in step.depends_on:
            dep_step = next((s for s in workflow.steps if s.step_id == dep_id), None)
            if not dep_step or dep_step.status != StepStatus.SUCCESS:
                return False
                
        # Future: Evaluate step.preconditions against system state here
            
        return True
        
    @staticmethod
    def skip_dependents(failed_step_id: str, workflow: Workflow) -> None:
        """Marks any step that depends on the failed step as SKIPPED (Cascading)."""
        for step in workflow.steps:
            if step.status == StepStatus.WAITING and failed_step_id in step.depends_on:
                step.status = StepStatus.SKIPPED
                # Recursively skip downstream dependents
                DependencyManager.skip_dependents(step.step_id, workflow)
