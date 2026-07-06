from typing import Optional, Dict, Any
from pydantic import BaseModel
from src.models.target import Target
from src.models.ui_element import UIElement

class InteractionContext(BaseModel):
    """
    The singular truth passed to every Automation tool.
    Completely replaces passing arbitrary string arguments.
    """
    current_target: Optional[Target] = None
    focused_element: Optional[UIElement] = None
    selected_element: Optional[UIElement] = None
    cursor_position: Optional[str] = None
    selection_text: Optional[str] = None
    backend: str = "windows"
    
    metadata: Dict[str, Any] = {}
