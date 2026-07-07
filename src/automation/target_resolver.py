from typing import Optional
from src.models.target import InteractionTarget
from src.automation.interaction_manager import InteractionManager

class TargetResolver:
    """
    Resolves higher-level target queries into specific, interactive targets 
    by walking the InteractionGraph.
    """
    def __init__(self):
        self.manager = InteractionManager()
        
    def resolve_primary_edit(self, base_target_id: str) -> Optional[InteractionTarget]:
        """
        Finds the primary editable child control within a given base target.
        """
        def is_editable(node: InteractionTarget) -> bool:
            # In reality, this would query the CapabilityProvider or check TargetSession capabilities.
            # For now, we use a simple heuristic based on the ID or name for demonstration.
            return "edit" in node.friendly_name.lower() or "document" in node.friendly_name.lower() or node.id.startswith("target_control")
            
        return self.manager._graph.find_node_by_predicate(is_editable, start_node_id=base_target_id)
