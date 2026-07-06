from abc import ABC, abstractmethod
from typing import Optional, Any
from src.models.ui_element import UIElementHandle

class AutomationDriver(ABC):
    """Abstract interface for all UI Automation Backends (Windows, Playwright, AT-SPI, Mac, Vision)."""
    
    @property
    @abstractmethod
    def driver_name(self) -> str:
        pass

    @abstractmethod
    def find_window(self, name: str, class_name: str = None) -> Optional[UIElementHandle]:
        pass
        
    @abstractmethod
    def find_element(self, window: UIElementHandle, locator_strategy: Any, query: str) -> Optional[UIElementHandle]:
        pass
        
    @abstractmethod
    def click(self, element: UIElementHandle, double: bool = False, right: bool = False) -> bool:
        pass
        
    @abstractmethod
    def type_text(self, element: UIElementHandle, text: str, clear_first: bool = False) -> bool:
        pass
        
    @abstractmethod
    def focus(self, element: UIElementHandle) -> bool:
        pass
        
    @abstractmethod
    def scroll(self, element: UIElementHandle, direction: str, amount: int) -> bool:
        pass
        
    @abstractmethod
    def read_text(self, element: UIElementHandle) -> str:
        pass
        
    @abstractmethod
    def capture(self, element: Optional[UIElementHandle] = None) -> str:
        """Returns the path to the captured screenshot."""
        pass
        
    @abstractmethod
    def build_tree_cache(self, window: UIElementHandle) -> Any:
        pass
