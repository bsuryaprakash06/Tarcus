from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime

class ExecutionEvent(BaseModel):
    """Base class for all execution-related events."""
    timestamp: datetime = datetime.utcnow()
    workflow_id: str

class WorkflowStarted(ExecutionEvent):
    goal: str

class WorkflowCompleted(ExecutionEvent):
    duration_sec: float

class WorkflowPaused(ExecutionEvent):
    reason: str

class WorkflowResumed(ExecutionEvent):
    pass

class WorkflowFailed(ExecutionEvent):
    error: str

class StepStarted(ExecutionEvent):
    step_id: str
    tool: str

class StepCompleted(ExecutionEvent):
    step_id: str
    tool: str
    result: Any

class StepFailed(ExecutionEvent):
    step_id: str
    tool: str
    error: str
    will_retry: bool

class StepVerified(ExecutionEvent):
    step_id: str
    strategy: str

class StepVerificationFailed(ExecutionEvent):
    step_id: str
    strategy: str
    reason: str

class PreconditionFailed(ExecutionEvent):
    step_id: str
    precondition_type: str
    reason: str
    
class PreconditionRecovered(ExecutionEvent):
    step_id: str
    precondition_type: str
