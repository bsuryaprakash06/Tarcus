import pytest
from unittest.mock import MagicMock, patch
from src.models.workflow_execution import ExecutionWorkflow, ExecutionStep, ExecutionState, Precondition
from src.execution.execution_controller import ExecutionController
from src.execution.action_executor import ActionExecutor
from src.execution.workflow_builder import WorkflowBuilder
from src.execution.execution_planner import ExecutionPlanner
from src.models.plan import ExecutionPlan, PlanItem

def test_workflow_builder():
    builder = WorkflowBuilder()
    plan = ExecutionPlan(plan=[
        PlanItem(tool="open_application", arguments={"application": "notepad"}),
        PlanItem(tool="type_text", arguments={"text": "hello"})
    ])
    
    workflow = builder.build_workflow("Open notepad and type hello", plan)
    assert len(workflow.steps) == 2
    assert workflow.steps[0].tool == "open_application"
    assert workflow.steps[1].tool == "type_text"
    assert workflow.goal == "Open notepad and type hello"
    assert workflow.status == ExecutionState.PENDING

def test_execution_planner():
    builder = WorkflowBuilder()
    plan = ExecutionPlan(plan=[
        PlanItem(tool="open_application", arguments={}),
        PlanItem(tool="type_text", arguments={})
    ])
    workflow = builder.build_workflow("Test", plan)
    
    planner = ExecutionPlanner()
    augmented_workflow = planner.plan_execution(workflow)
    
    # open_application step
    assert len(augmented_workflow.steps[0].verification) == 1
    assert augmented_workflow.steps[0].verification[0].strategy == "OpenApplicationVerifier"
    assert augmented_workflow.steps[0].max_retries == 3
    
    # type_text step
    assert len(augmented_workflow.steps[1].preconditions) == 2
    assert augmented_workflow.steps[1].preconditions[0].type == "WINDOW_FOCUSED"

@patch('src.execution.action_executor.ExecutorService')
@patch('src.execution.action_executor.PreconditionChecker')
def test_action_executor_success(MockPreconditionChecker, MockExecutorService):
    mock_checker = MockPreconditionChecker.return_value
    mock_checker.check_and_recover.return_value = (True, "")
    
    mock_service = MockExecutorService.return_value
    mock_service.execute_tool.return_value = "Success"
    
    executor = ActionExecutor()
    executor.precondition_checker = mock_checker
    executor.executor_service = mock_service
    
    step = ExecutionStep(step_id="123", tool="open_application")
    
    success = executor.execute_step(step, "wf_123", {})
    assert success is True
    assert step.status == ExecutionState.COMPLETED
    mock_service.execute_tool.assert_called_once_with("open_application")

@patch('src.execution.action_executor.PreconditionChecker')
def test_action_executor_precondition_failure(MockPreconditionChecker):
    mock_checker = MockPreconditionChecker.return_value
    mock_checker.check_and_recover.return_value = (False, "Target not found")
    
    executor = ActionExecutor()
    executor.precondition_checker = mock_checker
    
    step = ExecutionStep(
        step_id="123", 
        tool="type_text",
        max_retries=1,
        preconditions=[Precondition(type="WINDOW_EXISTS")]
    )
    
    success = executor.execute_step(step, "wf_123", {})
    assert success is False
    assert step.status == ExecutionState.FAILED
    assert step.error_message == "Preconditions failed after max retries"
    # It should have tried attempt 0 and attempt 1 (2 calls)
    assert mock_checker.check_and_recover.call_count == 2
