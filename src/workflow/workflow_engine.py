import time
import uuid
from typing import Optional

from src.models.plan import ExecutionPlan
from src.models.workflow import Workflow, WorkflowStep, WorkflowStatus, StepStatus, FailurePolicy
from src.workflow.workflow_events import WorkflowEventBus, WorkflowEventType
from src.workflow.dependency_manager import DependencyManager
from src.workflow.retry_manager import RetryManager
from src.workflow.workflow_state_manager import WorkflowStateManager
from src.workflow.cancellation_manager import CancellationManager
from src.services.executor_service import ExecutorService
from src.utils.logger import get_logger

logger = get_logger("workflow.engine")

class WorkflowEngine:
    """The central orchestrator for multi-step execution, retries, pausing, and recovery."""
    
    def __init__(self):
        self.state_manager = WorkflowStateManager()
        self.cancellation_manager = CancellationManager()
        self.event_bus = WorkflowEventBus()
        self.executor = ExecutorService()
        
    def _create_workflow_from_plan(self, plan: ExecutionPlan) -> Workflow:
        """Converts a parsed LLM ExecutionPlan into a persistent Workflow model."""
        workflow_id = str(uuid.uuid4())
        context = self.executor.get_current_context()
        steps = []
        
        # Linear LLM plans are purely sequential by default
        previous_step_id = None
        for i, plan_item in enumerate(plan.plan):
            step_id = f"{workflow_id}-step-{i}"
            depends_on = [previous_step_id] if previous_step_id else []
            
            step = WorkflowStep(
                step_id=step_id,
                tool=plan_item.tool,
                arguments=plan_item.arguments,
                depends_on=depends_on
            )
            steps.append(step)
            previous_step_id = step_id
            
        return Workflow(
            workflow_id=workflow_id,
            execution_id=context.execution_id,
            steps=steps,
            total_steps=len(steps)
        )
        
    def initialize_workflow(self, plan: ExecutionPlan) -> Workflow:
        """Creates and serializes a new workflow from an LLM plan."""
        workflow = self._create_workflow_from_plan(plan)
        self.state_manager.save(workflow)
        return workflow
        
    def execute(self, workflow_id: str) -> None:
        """Runs a workflow synchronously, respecting dependencies, pauses, and cancellations."""
        workflow = self.state_manager.load(workflow_id)
        if not workflow:
            logger.error(f"Cannot execute. Workflow {workflow_id} not found on disk.")
            return
            
        workflow.status = WorkflowStatus.RUNNING
        self.state_manager.save(workflow)
        self.event_bus.publish(WorkflowEventType.WORKFLOW_STARTED, {"workflow_id": workflow_id})
        
        context = self.executor.get_current_context()
        context.execution_id = workflow.execution_id
        
        for index, step in enumerate(workflow.steps):
            workflow.current_step_index = index
            
            # 1. Check for manual interruptions (Pause / Cancel)
            interrupt = self.cancellation_manager.get_interrupt_request(workflow_id)
            if interrupt:
                workflow.status = interrupt
                self.state_manager.save(workflow)
                
                if interrupt == WorkflowStatus.PAUSED:
                    self.event_bus.publish(WorkflowEventType.WORKFLOW_PAUSED, {"workflow_id": workflow_id})
                elif interrupt == WorkflowStatus.CANCELLED:
                    self.event_bus.publish(WorkflowEventType.WORKFLOW_CANCELLED, {"workflow_id": workflow_id})
                    
                self.cancellation_manager.clear_request(workflow_id)
                return
                
            # 2. Skip already completed/failed steps (crucial for State Recovery)
            if step.status in (StepStatus.SUCCESS, StepStatus.SKIPPED, StepStatus.FAILED):
                continue
                
            # 3. Enforce Preconditions and Dependency Order
            if not DependencyManager.can_execute(step.step_id, workflow):
                logger.debug(f"Step {step.step_id} bypassed (Dependencies not met).")
                continue
                
            # 4. Execute the step (with safe retries)
            self._execute_step_with_retries(step, workflow, context)
            
            # 5. Handle Critical Failures
            if step.status == StepStatus.FAILED and step.failure_policy == FailurePolicy.ABORT:
                workflow.status = WorkflowStatus.FAILED
                self.state_manager.save(workflow)
                self.event_bus.publish(WorkflowEventType.WORKFLOW_FAILED, {"workflow_id": workflow_id})
                return
                
            # Snapshot state after every single step
            self.state_manager.save(workflow)
            
        # Determine final workflow status
        all_success_or_skipped = all(s.status in (StepStatus.SUCCESS, StepStatus.SKIPPED) for s in workflow.steps)
        if all_success_or_skipped:
            workflow.status = WorkflowStatus.COMPLETED
            self.event_bus.publish(WorkflowEventType.WORKFLOW_COMPLETED, {"workflow_id": workflow_id})
            # Keep the state file for history or delete it? We will keep it for now.
        else:
            workflow.status = WorkflowStatus.FAILED
            self.event_bus.publish(WorkflowEventType.WORKFLOW_FAILED, {"workflow_id": workflow_id})
            
        self.state_manager.save(workflow)
        
    def _execute_step_with_retries(self, step: WorkflowStep, workflow: Workflow, context) -> None:
        """Executes a single atomic step, deferring retry logic to the RetryManager."""
        while True:
            step.status = StepStatus.RUNNING
            self.state_manager.save(workflow)
            self.event_bus.publish(WorkflowEventType.STEP_STARTED, {"step_id": step.step_id, "tool": step.tool})
            
            result = self.executor.execute_step(step, context)
            step.result = result
            
            if result.success:
                step.status = StepStatus.SUCCESS
                self.event_bus.publish(WorkflowEventType.STEP_COMPLETED, {"step_id": step.step_id, "result": result.model_dump()})
                break
            else:
                if RetryManager.should_retry(step, result):
                    step.retry_count += 1
                    logger.warning(f"Retrying step {step.step_id} (Attempt {step.retry_count})")
                    self.event_bus.publish(WorkflowEventType.STEP_RETRY, {"step_id": step.step_id, "retry": step.retry_count})
                    time.sleep(1) # Brief breather before retrying
                    continue
                else:
                    step.status = StepStatus.FAILED
                    self.event_bus.publish(WorkflowEventType.STEP_FAILED, {"step_id": step.step_id, "error": result.user_message})
                    
                    if step.failure_policy == FailurePolicy.SKIP_DEPENDENTS:
                        DependencyManager.skip_dependents(step.step_id, workflow)
                    break
