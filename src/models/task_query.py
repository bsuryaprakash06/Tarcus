from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DependencyType(str, Enum):
    NONE = "NONE"
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class AtomicTask(BaseModel):
    """An atomic, fully contextualized request split from a larger multi-intent prompt."""
    id: str
    text: str
    order: int
    depends_on: Optional[List[str]] = Field(default_factory=list)
    dependency_type: DependencyType = DependencyType.NONE
    status: TaskStatus = TaskStatus.PENDING
    intent: Optional[str] = None

class ExecutionGraph(BaseModel):
    """The directed acyclic graph representing the user's overall multi-task intent."""
    tasks: List[AtomicTask] = Field(default_factory=list)
