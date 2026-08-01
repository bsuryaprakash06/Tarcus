from typing import Optional, List
from src.utils.logger import get_logger
from .browser_manager import BrowserManager
from .browser_models import BrowserInstance, BrowserSession, BrowserTab

logger = get_logger("browser.coordinator")

class BrowserCoordinator:
    """
    Sits between the Execution Controller and Browser Manager.
    Resolves sessions, handles active context synchronization, and high-level navigation validation.
    """
    def __init__(self, browser_manager: BrowserManager):
        self.manager = browser_manager
        self.active_browser_id: Optional[str] = None
        
    def resolve_active_browser(self) -> Optional[str]:
        if self.active_browser_id and self.manager.registry.get_instance(self.active_browser_id):
            return self.active_browser_id
            
        instances = self.manager.registry.list_instances()
        if instances:
            self.active_browser_id = instances[-1].id
            return self.active_browser_id
        return None

    def launch_and_set_active(self) -> BrowserInstance:
        instance = self.manager.launch()
        self.active_browser_id = instance.id
        logger.info(f"Coordinator set active browser to {instance.id}")
        return instance

    def navigate_active_tab(self, url: str) -> bool:
        browser_id = self.resolve_active_browser()
        if not browser_id:
            instance = self.launch_and_set_active()
            browser_id = instance.id
            
        session = self.manager.registry.get_session_for_browser(browser_id)
        if not session: return False
        
        tab_id = session.active_tab_id
        if not tab_id:
            tab = self.manager.create_tab(browser_id, url)
            return tab is not None
            
        return self.manager.navigate(browser_id, tab_id, url)
        
    def get_context(self) -> dict:
        browser_id = self.resolve_active_browser()
        if not browser_id:
            return {"active_browser": None, "active_tab": None, "active_url": None}
            
        session = self.manager.registry.get_session_for_browser(browser_id)
        if not session:
            return {"active_browser": browser_id, "active_tab": None, "active_url": None}
            
        tab_id = session.active_tab_id
        url = session.tabs[tab_id].url if tab_id and tab_id in session.tabs else None
        
        return {
            "active_browser": browser_id,
            "active_tab": tab_id,
            "active_url": url,
            "current_session": session.session_id,
            "history_length": len(session.history)
        }
