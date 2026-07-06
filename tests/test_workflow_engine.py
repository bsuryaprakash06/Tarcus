import pytest
import os
from src.models.plan import ExecutionPlan, PlanItem
from src.models.workflow import WorkflowStatus, StepStatus, FailurePolicy
from src.workflow.workflow_engine import WorkflowEngine
from src.workflow.dependency_manager import DependencyManager

def test_workflow_initialization_and_dependencies():
    engine = WorkflowEngine()
    plan = ExecutionPlan(
        plan=[
            PlanItem(tool="open_application", arguments={"application": "Notepad"}),
            PlanItem(tool="create_file", arguments={"name": "test.txt"})
        ]
    )
    
    workflow = engine.initialize_workflow(plan)
    assert len(workflow.steps) == 2
    assert workflow.steps[0].tool == "open_application"
    # Verify linear dependencies are auto-linked
    assert workflow.steps[1].depends_on == [workflow.steps[0].step_id]

def test_workflow_cancellation():
    engine = WorkflowEngine()
    plan = ExecutionPlan(
        plan=[
            PlanItem(tool="open_application", arguments={"application": "Notepad"}),
            PlanItem(tool="create_file", arguments={"name": "test.txt"})
        ]
    )
    
    workflow = engine.initialize_workflow(plan)
    
    # Simulate a cancellation request before execution begins
    engine.cancellation_manager.request_cancel(workflow.workflow_id)
    engine.execute(workflow.workflow_id)
    
    # Reload from state manager to verify state recovery logic
    reloaded = engine.state_manager.load(workflow.workflow_id)
    assert reloaded.status == WorkflowStatus.CANCELLED
    
def test_skip_dependents():
    engine = WorkflowEngine()
    plan = ExecutionPlan(
        plan=[
            PlanItem(tool="open_application", arguments={"application": "Notepad"}),
            PlanItem(tool="create_file", arguments={"name": "test.txt"})
        ]
    )
    
    workflow = engine.initialize_workflow(plan)
    
    # Simulate a failure on step 0
    workflow.steps[0].status = StepStatus.FAILED
    
    # Enforce skip dependencies logic
    DependencyManager.skip_dependents(workflow.steps[0].step_id, workflow)
    
    # Verify downstream dependent step was skipped without aborting the engine
    assert workflow.steps[1].status == StepStatus.SKIPPED
