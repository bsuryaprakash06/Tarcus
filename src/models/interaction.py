from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class InteractionCapability(str, Enum):
    TEXT_INPUT = "TEXT_INPUT"
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    RIGHT_CLICK = "RIGHT_CLICK"
    SCROLL = "SCROLL"
    SELECT = "SELECT"
    FOCUS = "FOCUS"
    READ = "READ"
    DRAG_DROP = "DRAG_DROP"
    COPY = "COPY"
    PASTE = "PASTE"
    SHORTCUT = "SHORTCUT"
    CUSTOM = "CUSTOM"

class InteractionConstraint(str, Enum):
    ENABLED = "ENABLED"
    VISIBLE = "VISIBLE"
    NOT_BUSY = "NOT_BUSY"
    EDITABLE = "EDITABLE"
    FOCUSED = "FOCUSED"
    EXPANDED = "EXPANDED"

class InteractionState(str, Enum):
    DISCOVERED = "DISCOVERED"
    AVAILABLE = "AVAILABLE"
    FOCUSED = "FOCUSED"
    LOCKED = "LOCKED"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"

class InteractionNode(BaseModel):
    """
    Universal interaction object returned by all backends (Windows, Browser, Vision).
    Acts as a node in the semantic Interaction Graph.
    """
    id: str
    platform: str = "windows"
    backend: str = "uiautomation"
    native_handle: Optional[str] = None
    
    # Graph Relationships
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    
    # Semantic Properties
    role: str = "unknown"
    name: str = ""
    description: str = ""
    visibility: bool = True
    confidence: float = 1.0 # Useful for Vision backend
    state: InteractionState = InteractionState.DISCOVERED
    
    # Capabilities and Constraints
    capabilities: List[InteractionCapability] = Field(default_factory=list)
    constraints: List[InteractionConstraint] = Field(default_factory=list)
    
    geometry: Optional[Dict[str, int]] = None # {"x": 0, "y": 0, "width": 100, "height": 20}
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InteractionWorkflowStep(BaseModel):
    action: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class InteractionWorkflow(BaseModel):
    """A deterministic sequence of actions (formerly InteractionPlan)."""
    goal: str
    target_node_id: str
    steps: List[InteractionWorkflowStep] = Field(default_factory=list)
    required_capabilities: List[InteractionCapability] = Field(default_factory=list)
    required_constraints: List[InteractionConstraint] = Field(default_factory=list)

# Hierarchical Sessions
class InteractionSession(BaseModel):
    """Lowest level scope: A specific interaction attempt on a node."""
    session_id: str
    node_id: str
    active_capabilities: List[InteractionCapability] = Field(default_factory=list)
    workflow_history: List[InteractionWorkflow] = Field(default_factory=list)

class WindowSession(BaseModel):
    """Mid-level scope: A specific window or tab."""
    session_id: str
    window_node_id: str
    active_interaction_sessions: Dict[str, InteractionSession] = Field(default_factory=dict)
    cached_controls: Dict[str, str] = Field(default_factory=dict) # Name -> node_id

class ApplicationSession(BaseModel):
    """Top-level scope: A specific running application (e.g. Chrome, Notepad)."""
    session_id: str
    app_node_id: str
    active_window_sessions: Dict[str, WindowSession] = Field(default_factory=dict)
