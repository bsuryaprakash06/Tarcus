from typing import List
import uuid
from src.models.plan import ExecutionPlan
from src.models.workflow import Workflow, WorkflowStep, WorkflowStatus, StepStatus, FailurePolicy
from src.utils.logger import get_logger

logger = get_logger("workflow.composer")

class WorkflowComposer:
    """Takes independent ExecutionPlans and stitches them together into a unified executable Workflow."""
    
    @staticmethod
    def compose(plans: List[ExecutionPlan]) -> Workflow:
        workflow = Workflow(
            workflow_id=str(uuid.uuid4()),
            execution_id=str(uuid.uuid4()),
            status=WorkflowStatus.PENDING,
            steps=[]
        )
        
        # Stitches every atomic node together into a massive linear workflow
        for plan in plans:
            for item in plan.plan:
                step = WorkflowStep(
                    step_id=str(uuid.uuid4()),
                    tool=item.tool,
                    arguments=item.arguments,
                    failure_policy=FailurePolicy.SKIP_DEPENDENTS
                )
                workflow.steps.append(step)
                
        logger.info(f"Composed master workflow with {len(workflow.steps)} steps from {len(plans)} atomic plans.")
        return workflow
