from abc import ABC, abstractmethod
from typing import Optional, List
from .browser_models import BrowserType

class BrowserProvider(ABC):
    """
    Abstract Base Interface for Browser Backends (e.g. Playwright, Selenium).
    """
    @abstractmethod
    def launch(self, browser_type: BrowserType, headless: bool = False, **kwargs) -> str:
        """Launches a browser and returns a unique browser_id."""
        pass

    @abstractmethod
    def close(self, browser_id: str) -> None:
        """Closes the specified browser instance."""
        pass
        
    @abstractmethod
    def create_tab(self, browser_id: str, url: str = "about:blank") -> str:
        """Creates a new tab/page and returns a unique tab_id."""
        pass
        
    @abstractmethod
    def close_tab(self, browser_id: str, tab_id: str) -> None:
        """Closes a specific tab."""
        pass
        
    @abstractmethod
    def navigate(self, browser_id: str, tab_id: str, url: str, timeout: int = 30000) -> bool:
        """Navigates a specific tab to a URL."""
        pass
        
    @abstractmethod
    def refresh(self, browser_id: str, tab_id: str) -> bool:
        """Refreshes the specified tab."""
        pass
        
    @abstractmethod
    def get_url(self, browser_id: str, tab_id: str) -> str:
        """Returns the current URL of the specified tab."""
        pass
        
    @abstractmethod
    def get_title(self, browser_id: str, tab_id: str) -> str:
        """Returns the current title of the specified tab."""
        pass
