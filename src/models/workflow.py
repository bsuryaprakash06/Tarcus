from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.plan import ToolResult

class FailurePolicy(str, Enum):
    ABORT = "ABORT"               # Fail the entire workflow
    CONTINUE = "CONTINUE"         # Keep executing everything else
    SKIP_DEPENDENTS = "SKIP_DEPENDENTS" # Skip only downstream dependent steps

class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"

class StepStatus(str, Enum):
    WAITING = "WAITING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class WorkflowStep(BaseModel):
    """Represents a single atomic operation inside a workflow."""
    step_id: str
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    
    # State tracking
    status: StepStatus = StepStatus.WAITING
    retry_count: int = 0
    result: Optional[ToolResult] = None
    
    # Orchestration and Resiliency (Future-proofed)
    depends_on: List[str] = Field(default_factory=list, description="IDs of steps that must succeed first.")
    preconditions: List[str] = Field(default_factory=list, description="State preconditions (e.g. 'Internet Connected').")
    timeout: int = Field(default=30, description="Max execution time in seconds.")
    failure_policy: FailurePolicy = Field(default=FailurePolicy.SKIP_DEPENDENTS)
    rollback_step: Optional[str] = Field(default=None, description="Pointer to a step that reverts this operation.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary context for metrics and events.")

class Workflow(BaseModel):
    """The master orchestration container."""
    workflow_id: str
    parent_workflow_id: Optional[str] = None
    execution_id: str
    
    status: WorkflowStatus = WorkflowStatus.PENDING
    steps: List[WorkflowStep] = Field(default_factory=list)
    current_step_index: int = 0
    total_steps: int = 0
    
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = Field(default_factory=lambda: datetime.now().timestamp())
