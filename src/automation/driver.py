from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from src.models.target import InteractionTarget, TargetSession
from src.models.interaction_graph import InteractionGraph

class AutomationBackend(ABC):
    """
    Universal interface for all automation backends.
    All actions operate on a TargetSession and use InteractionStrategies internally.
    """
    
    @property
    @abstractmethod
    def backend_name(self) -> str:
        pass

    @abstractmethod
    def discover(self) -> InteractionGraph:
        """Polls the environment and returns an InteractionGraph of discovered targets."""
        pass
        
    @abstractmethod
    def resolve(self, session: TargetSession, query: str) -> Optional[InteractionTarget]:
        """Resolves a child target based on a query within the session's graph."""
        pass
        
    @abstractmethod
    def focus(self, session: TargetSession) -> bool:
        """Restores and brings the target to the absolute foreground."""
        pass

    @abstractmethod
    def click(self, session: TargetSession, double: bool = False, right: bool = False) -> bool:
        pass
        
    @abstractmethod
    def type(self, session: TargetSession, text: str, clear_first: bool = False) -> bool:
        pass
        
    @abstractmethod
    def read(self, session: TargetSession) -> str:
        pass
        
    @abstractmethod
    def scroll(self, session: TargetSession, direction: str, amount: int) -> bool:
        pass
        
    @abstractmethod
    def capture(self, session: TargetSession) -> str:
        """Returns a path or base64 string of the captured visual state."""
        pass
        
    @abstractmethod
    def verify(self, session: TargetSession, condition: Dict[str, Any]) -> bool:
        """Verifies a specific condition natively via the backend."""
        pass
