import uuid
from typing import List
from src.models.plan import ExecutionPlan
from src.models.workflow_execution import ExecutionWorkflow, ExecutionStep, ExecutionState
from src.utils.logger import get_logger

logger = get_logger("execution.workflow_builder")

class WorkflowBuilder:
    """
    Receives the logical plan from the semantic Brain Planner and strictly focuses 
    on assembling it into a structured sequence of actions.
    """
    
    def build_workflow(self, goal: str, plan: ExecutionPlan) -> ExecutionWorkflow:
        workflow_id = str(uuid.uuid4())
        workflow = ExecutionWorkflow(
            workflow_id=workflow_id,
            goal=goal,
            status=ExecutionState.PENDING
        )
        
        for item in plan.plan:
            step = ExecutionStep(
                step_id=str(uuid.uuid4()),
                tool=item.tool,
                arguments=item.arguments
            )
            workflow.steps.append(step)
            
        logger.info(f"WorkflowBuilder assembled {len(workflow.steps)} steps for goal: '{goal}'")
        return workflow
