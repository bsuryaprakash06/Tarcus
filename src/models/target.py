from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class TargetType(str, Enum):
    WINDOW = "WINDOW"
    BROWSER_TAB = "BROWSER_TAB"
    DOCUMENT = "DOCUMENT"
    CONTROL = "CONTROL"
    EDITABLE_ELEMENT = "EDITABLE_ELEMENT"
    PLUGIN_RESOURCE = "PLUGIN_RESOURCE"

class TargetLifecycle(str, Enum):
    DISCOVERED = "DISCOVERED"
    AVAILABLE = "AVAILABLE"
    ACTIVE = "ACTIVE"
    BUSY = "BUSY"
    MINIMIZED = "MINIMIZED"
    CLOSED = "CLOSED"

class TargetCapability(str, Enum):
    TYPING = "TYPING"
    CLICKING = "CLICKING"
    SCROLLING = "SCROLLING"
    READING = "READING"
    DRAGGING = "DRAGGING"
    SELECTION = "SELECTION"

class Target(BaseModel):
    """
    A globally unique abstraction of anything Tarcus can interact with.
    """
    id: str = Field(description="Globally unique ID (e.g., target_0001)")
    type: TargetType
    backend: str = Field(description="The automation backend handling this target (e.g., WINDOWS_UIA, PLAYWRIGHT)")
    name: str = Field(description="Human-readable name (e.g., 'Untitled - Notepad')")
    native_handle: Optional[str] = Field(default=None, description="Backend-specific reference ID")
    lifecycle_state: TargetLifecycle = TargetLifecycle.DISCOVERED
    capabilities: List[TargetCapability] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def can(self, capability: TargetCapability) -> bool:
        return capability in self.capabilities
