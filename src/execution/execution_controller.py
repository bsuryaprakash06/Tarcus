from typing import Dict, Any
from src.models.workflow_execution import ExecutionWorkflow, ExecutionState
from src.execution.state_tracker import StateTracker
from src.execution.action_executor import ActionExecutor
from src.services.context_service import ContextService
from src.events.pipeline_events import PipelineEventBus
from src.events.execution_events import WorkflowStarted, WorkflowCompleted, WorkflowFailed
from src.utils.logger import get_logger
from datetime import datetime

logger = get_logger("execution.execution_controller")

class ExecutionController:
    """
    Master engine for a single workflow. 
    Runs within a Scheduler thread. Advances through the workflow sequentially.
    Uses InteractionCoordinator for UI-centric steps.
    """
    
    def __init__(self, workflow: ExecutionWorkflow):
        self.workflow = workflow
        self.state_tracker = StateTracker(workflow)
        self.action_executor = ActionExecutor()
        self.context_service = ContextService()
        self.event_bus = PipelineEventBus()
        
    def run(self) -> bool:
        """Executes the workflow. Returns True if fully completed, False if failed/aborted."""
        self.event_bus.publish_event(WorkflowStarted(workflow_id=self.workflow.workflow_id, goal=self.workflow.goal))
        self.state_tracker.mark_workflow_status(ExecutionState.RUNNING)
        
        while True:
            step = self.state_tracker.get_current_step()
            if not step:
                break # All steps complete
                
            context = self.action_executor.executor_service.get_current_context()
            self.state_tracker.capture_before_snapshot(step, context)
            
            logger.info(f"ExecutionController running step: {step.step_id} ({step.tool})")
            
            # Check if this is a UI step that needs interaction coordination
            ui_tools = {"type_text": "typing", "click_element": "clicking", "scroll_element": "scrolling"}
            success = False
            
            # Execute Step
            if step.tool in ui_tools:
                from src.execution.interaction_coordinator import InteractionCoordinator
                from src.automation.windows_driver import WindowsDriver
                from src.automation.interaction_manager import InteractionManager
                
                driver = WindowsDriver()
                coordinator = InteractionCoordinator(driver, self.action_executor)
                intent = ui_tools[step.tool]
                
                manager = InteractionManager()
                sessions = manager.list_sessions(active_only=True)
                base_target_id = sessions[0].target.id if sessions else "desktop"
                
                success = coordinator.coordinate_interaction(intent, base_target_id, **step.arguments)
            else:
                success = self.action_executor.execute_step(step, self.workflow.workflow_id, context)
                
            # Verification Phase
            tool_instance = self.action_executor.executor_service.get_tool(step.tool)
            if tool_instance and hasattr(tool_instance, "metadata"):
                from src.verification.verification_manager import VerificationManager
                from src.verification.verification_provider import VerificationProvider
                from src.models.verification import VerificationStatus
                
                # Mock provider for now, would be injected realistically
                class MockProvider(VerificationProvider):
                    @property
                    def provider_name(self) -> str: return "MockWindows"
                    def evaluate(self, rule_name, session, context) -> bool: return True
                
                v_manager = VerificationManager(MockProvider())
                # For UI steps, we need a session. For now, pass None or basic object
                v_result = v_manager.verify(step.step_id, tool_instance.metadata, None, None)
                
                if v_result.status != VerificationStatus.SUCCESS:
                    logger.warning(f"Verification Failed. Entering RECOVERING state for step {step.step_id}")
                    step.status = ExecutionState.RECOVERING
                    
                    from src.verification.recovery_engine import RecoveryEngine
                    from src.automation.windows_driver import WindowsDriver
                    from src.models.verification import RecoveryStatus
                    from src.verification.retry_policy import RetryPolicyExecutor
                    
                    r_engine = RecoveryEngine(WindowsDriver())
                    # Attempt recovery
                    r_status = r_engine.attempt_recovery(step.step_id, None, tool_instance.metadata.recovery_policy)
                    
                    if r_status == RecoveryStatus.RECOVERED:
                        # Retry logic via policy
                        try:
                            # Simplistic retry integration
                            RetryPolicyExecutor.execute_with_retry(
                                lambda: self.action_executor.execute_step(step, self.workflow.workflow_id, context),
                                max_retries=tool_instance.metadata.recovery_policy.max_retries
                            )
                            logger.info(f"Step {step.step_id} successfully recovered and retried.")
                            success = True
                        except Exception as e:
                            logger.error(f"Retry failed: {e}")
                            success = False
                    else:
                        success = False
            
            new_context = self.action_executor.executor_service.get_current_context()
            self.state_tracker.capture_after_snapshot(step, new_context)
            
            if not success:
                logger.error(f"ExecutionController aborting workflow due to step {step.step_id} failure.")
                self.state_tracker.mark_workflow_status(ExecutionState.FAILED)
                self.workflow.completed_at = datetime.utcnow()
                
                self.event_bus.publish_event(WorkflowFailed(
                    workflow_id=self.workflow.workflow_id, 
                    error=f"Step {step.step_id} failed permanently."
                ))
                return False
                
            self.state_tracker.advance_step()
            
        self.state_tracker.mark_workflow_status(ExecutionState.COMPLETED)
        self.workflow.completed_at = datetime.utcnow()
        duration = (self.workflow.completed_at - self.workflow.created_at).total_seconds()
        self.event_bus.publish_event(WorkflowCompleted(workflow_id=self.workflow.workflow_id, duration_sec=duration))
        logger.info(f"ExecutionController successfully completed workflow {self.workflow.workflow_id}")
        return True
