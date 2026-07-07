from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field

class OverlayState(str, Enum):
    HIDDEN = "HIDDEN"
    VISIBLE = "VISIBLE"
    DISCOVERING = "DISCOVERING"
    VERIFYING = "VERIFYING"
    EXECUTING = "EXECUTING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    RECOVERING = "RECOVERING"
    THINKING = "THINKING"
    LOCKED = "LOCKED"

class ActionIndicatorType(str, Enum):
    CLICK = "CLICK"
    TYPE = "TYPE"
    READ = "READ"

class OverlayStyle(BaseModel):
    border_width: int = 2
    border_radius: int = 8
    glow_radius: int = 12
    opacity: float = 1.0

class OverlayTarget(BaseModel):
    """
    State model for a target currently being tracked by the overlay engine.
    Colors are resolved dynamically, not stored here.
    """
    interaction_target_id: str
    friendly_name: str
    current_state: OverlayState = OverlayState.VISIBLE
    badge_text: str = ""
    style: OverlayStyle = Field(default_factory=OverlayStyle)
    
    # Coordinates mapping from physical screen to the overlay
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
