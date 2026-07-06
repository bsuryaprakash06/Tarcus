from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ExecutionStrategy(str, Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    EXCLUSIVE = "EXCLUSIVE"
    BACKGROUND = "BACKGROUND"
    STREAMING = "STREAMING"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    CANCELLING = "CANCELLING"
    PAUSED = "PAUSED"
    RESUMING = "RESUMING"

class ResourceType(str, Enum):
    APPLICATION = "APPLICATION"
    BROWSER = "BROWSER"
    CLIPBOARD = "CLIPBOARD"
    FILESYSTEM = "FILESYSTEM"
    MICROPHONE = "MICROPHONE"
    SPEAKER = "SPEAKER"
    VISION_CAMERA = "VISION_CAMERA"

class ResourceLock(BaseModel):
    resource_type: ResourceType
    identifier: str = Field(description="E.g., 'Notepad' or 'Chrome'")
    exclusive: bool = True

class ExecutionNode(BaseModel):
    """
    A generic execution unit handled by the Scheduler. 
    It abstracts away whether this is an LLM workflow, a vision task, or a background job.
    """
    id: str
    handler_type: str = Field(description="E.g., 'AutomationHandler', 'KnowledgeHandler'")
    payload: Any = Field(description="The data passed to the handler (e.g., ExecutionPlan)")
    
    status: TaskStatus = TaskStatus.PENDING
    execution_strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    priority: int = 1
    
    dependencies: List[str] = Field(default_factory=list, description="IDs of nodes that must complete first")
    resource_requirements: List[ResourceLock] = Field(default_factory=list)
    
    result: Optional[Any] = None
    error: Optional[str] = None
    
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class TaskGraph(BaseModel):
    nodes: Dict[str, ExecutionNode] = Field(default_factory=dict)
    
    def add_node(self, node: ExecutionNode):
        self.nodes[node.id] = node
        
    def get_ready_nodes(self) -> List[ExecutionNode]:
        ready = []
        for node in self.nodes.values():
            if node.status in (TaskStatus.PENDING, TaskStatus.WAITING):
                # Check dependencies
                all_met = all(self.nodes[dep].status == TaskStatus.COMPLETED for dep in node.dependencies if dep in self.nodes)
                if all_met:
                    ready.append(node)
        return ready
