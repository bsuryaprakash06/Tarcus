from src.models.workflow_execution import ExecutionWorkflow, Precondition, VerificationRule, RollbackAction
from src.utils.logger import get_logger

logger = get_logger("execution.execution_planner")

class ExecutionPlanner:
    """
    Analyzes logical workflows and injects robust deterministic metadata 
    directly into the ExecutionSteps: Preconditions, VerificationStrategies, and RollbackActions.
    """
    
    def plan_execution(self, workflow: ExecutionWorkflow) -> ExecutionWorkflow:
        for step in workflow.steps:
            if step.tool == "type_text":
                pass
                # step.preconditions.append(Precondition(type="WINDOW_FOCUSED"))
                # step.preconditions.append(Precondition(type="TARGET_CAPABLE", parameters={"capability": "TYPING"}))
                # step.verification.append(VerificationRule(strategy="TypeTextVerifier"))
                
            elif step.tool == "open_application":
                step.verification.append(VerificationRule(strategy="OpenApplicationVerifier"))
                
            elif step.tool == "click_element":
                step.preconditions.append(Precondition(type="WINDOW_EXISTS"))
                step.preconditions.append(Precondition(type="TARGET_CAPABLE", parameters={"capability": "CLICKABLE"}))
                
            elif step.tool == "copy_clipboard":
                # Example Rollback
                step.rollback_action = RollbackAction(tool="restore_clipboard")
                
            # etc...
            
            # Default retries based on tool type
            if step.tool in ["open_application", "open_website"]:
                step.max_retries = 3
                step.timeout = 15.0
                
        logger.info(f"ExecutionPlanner augmented workflow {workflow.workflow_id} with deterministic rules.")
        return workflow
