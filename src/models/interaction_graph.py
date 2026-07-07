from typing import Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from src.models.target import InteractionTarget

class InteractionGraph(BaseModel):
    """
    Represents the hierarchical relationship between interaction targets (e.g., DOM, Window Tree).
    This graph is typically populated by the TargetResolver or CapabilityProvider.
    """
    root_id: str
    nodes: Dict[str, InteractionTarget] = Field(default_factory=dict)
    edges: Dict[str, List[str]] = Field(default_factory=dict) # parent_id -> [child_ids]
    
    def add_node(self, target: InteractionTarget, parent_id: Optional[str] = None):
        self.nodes[target.id] = target
        if parent_id:
            if parent_id not in self.edges:
                self.edges[parent_id] = []
            if target.id not in self.edges[parent_id]:
                self.edges[parent_id].append(target.id)
                
    def get_children(self, node_id: str) -> List[InteractionTarget]:
        child_ids = self.edges.get(node_id, [])
        return [self.nodes[cid] for cid in child_ids if cid in self.nodes]
        
    def find_node_by_predicate(self, predicate: Callable[[InteractionTarget], bool], start_node_id: Optional[str] = None) -> Optional[InteractionTarget]:
        """Breadth-first search for a node matching the predicate."""
        queue = [start_node_id or self.root_id]
        visited = set()
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            
            node = self.nodes.get(current_id)
            if node and predicate(node):
                return node
                
            queue.extend(self.edges.get(current_id, []))
            
        return None
