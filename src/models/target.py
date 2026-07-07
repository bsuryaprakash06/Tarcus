from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class Platform(str, Enum):
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"
    MACOS = "MACOS"
    ANDROID = "ANDROID"
    BROWSER = "BROWSER"
    VISION = "VISION"

class TargetState(str, Enum):
    ACTIVE = "ACTIVE"
    BACKGROUND = "BACKGROUND"
    MINIMIZED = "MINIMIZED"
    CLOSED = "CLOSED"
    UNKNOWN = "UNKNOWN"
    BUSY = "BUSY"

class VerificationResult(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

class TargetCapability(str, Enum):
    TYPING = "TYPING"
    CLICKING = "CLICKING"
    SCROLLING = "SCROLLING"
    READING = "READING"
    DRAGGING = "DRAGGING"
    SELECTION = "SELECTION"

class InteractionTarget(BaseModel):
    """
    An immutable representation of a real-world interaction target.
    Does NOT store runtime state.
    """
    id: str = Field(description="Semantic ID (e.g., target_notepad_8fd2)")
    platform: Platform = Field(description="Target platform")
    backend: str = Field(description="The automation backend (e.g., WINDOWS_UIA, PLAYWRIGHT)")
    native_handle: Optional[str] = Field(default=None, description="Backend-specific reference ID")
    pid: Optional[int] = Field(default=None, description="Process ID if applicable")
    friendly_name: str = Field(description="Human-readable name")
    
    class Config:
        frozen = True # Makes it immutable in pydantic

class TargetSession(BaseModel):
    """
    The runtime state wrapper around an InteractionTarget.
    """
    target: InteractionTarget
    state: TargetState = TargetState.UNKNOWN
    verification_result: VerificationResult = VerificationResult.UNKNOWN
    capabilities: List[TargetCapability] = Field(default_factory=list)
    cached_controls: Dict[str, InteractionTarget] = Field(default_factory=dict)
    timeline: List[str] = Field(default_factory=list)
    resource_lock: Optional[str] = Field(default=None, description="Lock ID if currently exclusively locked by a workflow")
    
    def can(self, capability: TargetCapability) -> bool:
        return capability in self.capabilities
    
    def record_interaction(self, action: str):
        self.timeline.append(action)
