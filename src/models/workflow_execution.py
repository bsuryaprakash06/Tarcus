from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

class ExecutionState(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    VERIFYING = "VERIFYING"
    RETRYING = "RETRYING"
    RECOVERING = "RECOVERING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"

class Precondition(BaseModel):
    """A requirement that must be met before a step executes."""
    type: str  # e.g., "WINDOW_EXISTS", "TARGET_CAPABLE", "CLIPBOARD_READY"
    target_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)

class VerificationRule(BaseModel):
    """A rule applied after execution to ensure success."""
    strategy: str  # e.g., "OpenApplicationVerifier", "ClickVerifier"
    parameters: Dict[str, Any] = Field(default_factory=dict)

class RollbackAction(BaseModel):
    """Action to take to undo a step if the workflow fails later."""
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class StateSnapshot(BaseModel):
    """A snapshot of the interaction context before and after execution."""
    before: Dict[str, Any] = Field(default_factory=dict)
    after: Dict[str, Any] = Field(default_factory=dict)

class ExecutionStep(BaseModel):
    """A single deterministic step within an ExecutionWorkflow."""
    step_id: str
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    
    preconditions: List[Precondition] = Field(default_factory=list)
    verification: List[VerificationRule] = Field(default_factory=list)
    rollback_action: Optional[RollbackAction] = None
    
    status: ExecutionState = ExecutionState.PENDING
    retry_count: int = 0
    max_retries: int = 2
    timeout: float = 30.0
    
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    snapshot: Optional[StateSnapshot] = None
    error_message: Optional[str] = None

class ExecutionWorkflow(BaseModel):
    """A complete workflow directed at achieving a specific user goal."""
    workflow_id: str
    goal: str
    steps: List[ExecutionStep] = Field(default_factory=list)
    current_step_index: int = 0
    status: ExecutionState = ExecutionState.PENDING
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    execution_history: List[Dict[str, Any]] = Field(default_factory=list)
