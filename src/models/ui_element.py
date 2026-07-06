from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime

class UIAction(str, Enum):
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    RIGHT_CLICK = "RIGHT_CLICK"
    TYPE = "TYPE"
    SELECT = "SELECT"
    SCROLL = "SCROLL"
    FOCUS = "FOCUS"
    READ_TEXT = "READ_TEXT"
    HOVER = "HOVER"

class UIElement(BaseModel):
    """Semantic representation of a GUI element."""
    id: str
    name: str
    automation_id: str = ""
    class_name: str = ""
    control_type: str = ""
    bounding_rectangle: Optional[List[int]] = None # [left, top, right, bottom]
    enabled: bool = True
    visible: bool = True
    focused: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UIElementHandle(BaseModel):
    """
    Caches the backend reference to avoid re-scanning the UI tree 
    for subsequent actions (e.g. 'Click it again').
    """
    backend_reference: Any = Field(exclude=True) # Cannot serialize backend UI objects
    cached_locator: str = ""
    ui_element: UIElement
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    
    class Config:
        arbitrary_types_allowed = True

class AutomationResult(BaseModel):
    """The result of executing a UI Automation Action."""
    success: bool
    duration: float
    element: Optional[UIElement] = None
    backend: str = "windows"
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
