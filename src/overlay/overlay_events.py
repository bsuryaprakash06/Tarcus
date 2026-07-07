from pydantic import BaseModel
from typing import Optional
from src.models.overlay import OverlayState, ActionIndicatorType

class OverlayCreated(BaseModel):
    interaction_target_id: str
    friendly_name: str
    initial_state: OverlayState = OverlayState.VISIBLE

class OverlayDestroyed(BaseModel):
    interaction_target_id: str

class OverlayShown(BaseModel):
    interaction_target_id: str

class OverlayHidden(BaseModel):
    interaction_target_id: str

class OverlayStateChanged(BaseModel):
    interaction_target_id: str
    new_state: OverlayState

class OverlayActionTriggered(BaseModel):
    interaction_target_id: str
    action_type: ActionIndicatorType
    
class OverlayBoundsUpdated(BaseModel):
    interaction_target_id: str
    x: int
    y: int
    width: int
    height: int
