from typing import Dict, Optional, List
from src.models.interaction import InteractionNode
from src.events.pipeline_events import PipelineEventBus
from src.interaction.interaction_events import GraphRefreshed
from src.utils.logger import get_logger

logger = get_logger("interaction.graph")

class InteractionGraph:
    """
    A persistent knowledge graph representing the semantic hierarchy of the active environments.
    Supports incremental branch refreshes and fast node lookups.
    """
    def __init__(self):
        self.nodes: Dict[str, InteractionNode] = {}
        self.event_bus = PipelineEventBus()

    def add_node(self, node: InteractionNode):
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[InteractionNode]:
        return self.nodes.get(node_id)

    def remove_node(self, node_id: str):
        if node_id in self.nodes:
            # Recursively remove children
            children = list(self.nodes[node_id].children_ids)
            for child_id in children:
                self.remove_node(child_id)
            del self.nodes[node_id]

    def update_branch(self, root_node: InteractionNode, flattened_descendants: List[InteractionNode]):
        """
        Incrementally refreshes a specific branch of the graph (e.g. a specific window).
        Removes stale children and updates the active ones.
        """
        # Remove old branch recursively to prevent stale nodes
        if root_node.id in self.nodes:
            old_children = self.nodes[root_node.id].children_ids
            for child_id in old_children:
                self.remove_node(child_id)
                
        self.add_node(root_node)
        for node in flattened_descendants:
            self.add_node(node)
            
        logger.debug(f"Refreshed graph branch at root: {root_node.id} with {len(flattened_descendants)} descendants.")
        self.event_bus.publish_event(GraphRefreshed(root_node_id=root_node.id, nodes_updated=len(flattened_descendants)+1))

    def search_by_role(self, role: str) -> List[InteractionNode]:
        return [n for n in self.nodes.values() if n.role.lower() == role.lower()]

    def search_by_name(self, name: str) -> List[InteractionNode]:
        return [n for n in self.nodes.values() if name.lower() in n.name.lower()]
