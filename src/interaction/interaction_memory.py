from typing import Optional, Dict
from src.models.interaction import InteractionNode
from src.events.pipeline_events import PipelineEventBus
from src.interaction.interaction_events import InteractionCached
from src.utils.logger import get_logger

logger = get_logger("interaction.memory")

class InteractionMemory:
    """
    Scoped semantic memory (Application -> Window -> Control).
    Hooks into the Dialogue Manager to resolve conversational references like 
    'Continue typing' or 'Click it' instantly without re-traversing the UI.
    """
    def __init__(self):
        # Current Active Scope
        self.active_app_node: Optional[InteractionNode] = None
        self.active_window_node: Optional[InteractionNode] = None
        self.active_control_node: Optional[InteractionNode] = None
        
        self.event_bus = PipelineEventBus()

    def set_active_app(self, node: InteractionNode):
        self.active_app_node = node
        self.event_bus.publish_event(InteractionCached(node_id=node.id, scope="Application"))

    def set_active_window(self, node: InteractionNode):
        self.active_window_node = node
        self.event_bus.publish_event(InteractionCached(node_id=node.id, scope="Window"))

    def set_active_control(self, node: InteractionNode):
        self.active_control_node = node
        self.event_bus.publish_event(InteractionCached(node_id=node.id, scope="Control"))

    def get_context(self) -> Dict[str, Optional[InteractionNode]]:
        """Returns the current semantic scope."""
        return {
            "app": self.active_app_node,
            "window": self.active_window_node,
            "control": self.active_control_node
        }

    def clear(self):
        self.active_app_node = None
        self.active_window_node = None
        self.active_control_node = None
