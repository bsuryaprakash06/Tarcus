from typing import Dict, Any
from src.models.workflow_execution import ExecutionStep, ExecutionState
from src.models.plan import ExecutionContext
from src.services.executor_service import ExecutorService
from src.events.pipeline_events import PipelineEventBus
from src.events.execution_events import StepStarted, StepCompleted, StepFailed
from src.models.target import TargetSession
from src.execution.interaction_planner import InteractionPlan
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger("execution.action_executor")

class ActionExecutor:
    """
    Middleware that invokes tools through the ExecutorService.
    Now separated from Interaction lifecycle orchestration.
    """
    def __init__(self):
        self.executor_service = ExecutorService()
        self.event_bus = PipelineEventBus()
        
    def execute_interaction_plan(self, session: TargetSession, plan: InteractionPlan, **kwargs) -> bool:
        """Executes tool-invocation operations defined in an InteractionPlan."""
        tool_name = ""
        if "insert" in plan.steps:
            tool_name = "type_text"
        elif "click" in plan.steps:
            tool_name = "click_element"
            
        if tool_name:
            logger.info(f"ActionExecutor invoking {tool_name} for InteractionPlan.")
            try:
                from src.tools.registry import get_tool
                tool = get_tool(tool_name)
                if tool:
                    # In this architecture, we pass the TargetSession as context!
                    res = tool.execute(kwargs, context=session) 
                    return res.success
                return False
            except Exception as e:
                logger.error(f"ActionExecutor failed to invoke {tool_name}: {e}")
                return False
        return True

    def execute_step(self, step: ExecutionStep, workflow_id: str, context: ExecutionContext) -> bool:
        """Executes a standard non-UI workflow step."""
        self.event_bus.publish_event(StepStarted(workflow_id=workflow_id, step_id=step.step_id, tool=step.tool))
        step.status = ExecutionState.RUNNING
        step.started_at = datetime.utcnow()
        
        try:
            logger.debug(f"ActionExecutor invoking {step.tool}")
            result = self.executor_service.execute_step(step, context)
            if "FAILED" in str(result):
                step.status = ExecutionState.FAILED
                step.error_message = str(result)
                return False
            
            step.status = ExecutionState.COMPLETED
            step.completed_at = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Execution crashed: {e}")
            step.status = ExecutionState.FAILED
            step.error_message = str(e)
            return False
