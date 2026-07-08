from pydantic import BaseModel
from typing import Any, Optional, Dict
from datetime import datetime

class InteractionEvent(BaseModel):
    timestamp: datetime = datetime.utcnow()

class InteractionResolved(InteractionEvent):
    goal: str
    node_id: str
    confidence: float
    source: str # "Dialogue Context", "Interaction Memory", "Interaction Graph", "Automation Backend"

class InteractionCached(InteractionEvent):
    node_id: str
    scope: str # "Application", "Window", "Control"

class InteractionExpired(InteractionEvent):
    node_id: str

class InteractionRecovered(InteractionEvent):
    node_id: str
    strategy: str

class InteractionUpdated(InteractionEvent):
    node_id: str
    changes: Dict[str, Any]

class GraphRefreshed(InteractionEvent):
    root_node_id: str
    nodes_updated: int
