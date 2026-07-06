from abc import ABC, abstractmethod
from typing import Optional, Any, List
from src.models.target import Target
from src.models.interaction import InteractionContext
from src.models.ui_element import UIElementHandle

class AutomationBackend(ABC):
    """
    Universal interface for all automation backends.
    All actions operate on a resolved Target within an InteractionContext.
    """
    
    @property
    @abstractmethod
    def backend_name(self) -> str:
        pass

    @abstractmethod
    def discover_targets(self) -> List[Target]:
        """Polls the environment and returns a list of discovered/active targets."""
        pass
        
    @abstractmethod
    def activate_target(self, target: Target) -> bool:
        """Restores and brings the target to the absolute foreground."""
        pass

    @abstractmethod
    def find_element(self, context: InteractionContext, query: str) -> Optional[UIElementHandle]:
        pass
        
    @abstractmethod
    def click(self, context: InteractionContext, double: bool = False, right: bool = False) -> bool:
        pass
        
    @abstractmethod
    def type_text(self, context: InteractionContext, text: str, clear_first: bool = False) -> bool:
        pass
        
    @abstractmethod
    def focus_element(self, context: InteractionContext) -> bool:
        pass
        
    @abstractmethod
    def scroll(self, context: InteractionContext, direction: str, amount: int) -> bool:
        pass
        
    @abstractmethod
    def read_text(self, context: InteractionContext) -> str:
        pass
        
    @abstractmethod
    def capture(self, context: InteractionContext) -> str:
        pass
