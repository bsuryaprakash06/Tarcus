import pytest
from src.models.plan import ExecutionPlan, PlanItem
from src.workflow.workflow_composer import WorkflowComposer
from src.models.workflow import StepStatus, FailurePolicy

def test_workflow_composer_stitching():
    plan1 = ExecutionPlan(
        plan=[PlanItem(tool="notepad", arguments={})]
    )
    plan2 = ExecutionPlan(
        plan=[PlanItem(tool="type", arguments={})]
    )
    
    workflow = WorkflowComposer.compose([plan1, plan2])
    
    assert workflow.status == "PENDING"
    assert len(workflow.steps) == 2
    
    assert workflow.steps[0].tool == "notepad"
    assert workflow.steps[0].failure_policy == FailurePolicy.SKIP_DEPENDENTS
    
    assert workflow.steps[1].tool == "type"
