from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from src.models.interaction import InteractionNode, InteractionWorkflowStep

class AutomationBackend(ABC):
    """
    Universal interface for all automation backends.
    Now standardized for the Semantic Interaction Engine.
    """
    
    @property
    @abstractmethod
    def backend_name(self) -> str:
        pass

    @abstractmethod
    def discover(self) -> InteractionNode:
        """Polls the environment and returns the root InteractionNode."""
        pass
        
    @abstractmethod
    def resolve(self, query: str) -> Optional[InteractionNode]:
        """Resolves a target node natively based on a query."""
        pass
        
    @abstractmethod
    def execute(self, node_id: str, step: InteractionWorkflowStep) -> bool:
        """Executes a single workflow step on the target node natively."""
        pass

    @abstractmethod
    def verify(self, node_id: str, condition: Dict[str, Any]) -> bool:
        """Verifies a specific condition natively via the backend."""
        pass
        
    @abstractmethod
    def refresh(self, node_id: str) -> Tuple[Optional[InteractionNode], List[InteractionNode]]:
        """
        Refreshes a specific branch of the native UI. 
        Returns (Updated Root Node, Flattened List of all Descendants).
        """
        pass
        
    @abstractmethod
    def destroy(self):
        """Cleans up native resources."""
        pass

    @abstractmethod
    def get_bounds(self, target_id: str) -> Optional[tuple[int, int, int, int]]:
        """Returns the current screen bounding box (x, y, width, height) of the target."""
        pass
        
    @abstractmethod
    def subscribe_to_window_events(self, callback) -> bool:
        """Subscribes to native window OS events (move, resize, visibility)."""
        pass
