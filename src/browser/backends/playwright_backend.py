from typing import Optional, Dict, Any
from src.utils.logger import get_logger
from ..browser_provider import BrowserProvider
from ..browser_models import BrowserType

logger = get_logger("browser.playwright_backend")

class PlaywrightBackend(BrowserProvider):
    """
    Playwright implementation of the BrowserProvider.
    Uses the synchronous Playwright API for deterministic execution.
    """
    def __init__(self):
        self._playwright = None
        self._browsers: Dict[str, Any] = {} # browser_id -> Browser instance
        self._contexts: Dict[str, Any] = {} # browser_id -> BrowserContext
        self._pages: Dict[str, Any] = {}    # tab_id -> Page instance
        self._tab_browser_map: Dict[str, str] = {} # tab_id -> browser_id

    def _ensure_started(self):
        if self._playwright is None:
            from playwright.sync_api import sync_playwright
            # We keep the playwright context alive indefinitely
            # In a real daemon, you might manage context lifecycle tighter
            self._pw_manager = sync_playwright()
            self._playwright = self._pw_manager.start()
            logger.info("Playwright sync API started.")

    def launch(self, browser_type: BrowserType, headless: bool = False, **kwargs) -> str:
        self._ensure_started()
        
        if browser_type == BrowserType.CHROMIUM:
            launcher = self._playwright.chromium
        elif browser_type == BrowserType.FIREFOX:
            launcher = self._playwright.firefox
        elif browser_type == BrowserType.WEBKIT:
            launcher = self._playwright.webkit
        else:
            launcher = self._playwright.chromium
            
        import uuid
        browser_id = f"browser_{uuid.uuid4().hex[:8]}"
        
        browser = launcher.launch(headless=headless)
        context = browser.new_context()
        
        self._browsers[browser_id] = browser
        self._contexts[browser_id] = context
        
        logger.info(f"Launched {browser_type.value} browser: {browser_id}")
        return browser_id

    def close(self, browser_id: str) -> None:
        if browser_id in self._browsers:
            self._contexts[browser_id].close()
            self._browsers[browser_id].close()
            del self._contexts[browser_id]
            del self._browsers[browser_id]
            
            # Clean up associated tabs
            tabs_to_remove = [t_id for t_id, b_id in self._tab_browser_map.items() if b_id == browser_id]
            for t_id in tabs_to_remove:
                if t_id in self._pages: del self._pages[t_id]
                del self._tab_browser_map[t_id]
                
            logger.info(f"Closed browser: {browser_id}")

    def create_tab(self, browser_id: str, url: str = "about:blank") -> str:
        if browser_id not in self._contexts:
            raise ValueError(f"Browser {browser_id} not found.")
            
        import uuid
        tab_id = f"tab_{uuid.uuid4().hex[:8]}"
        
        context = self._contexts[browser_id]
        page = context.new_page()
        page.goto(url)
        
        self._pages[tab_id] = page
        self._tab_browser_map[tab_id] = browser_id
        
        logger.info(f"Created tab {tab_id} in {browser_id}")
        return tab_id

    def close_tab(self, browser_id: str, tab_id: str) -> None:
        if tab_id in self._pages:
            self._pages[tab_id].close()
            del self._pages[tab_id]
            del self._tab_browser_map[tab_id]
            logger.info(f"Closed tab {tab_id}")

    def navigate(self, browser_id: str, tab_id: str, url: str, timeout: int = 30000) -> bool:
        if tab_id not in self._pages:
            return False
            
        try:
            page = self._pages[tab_id]
            page.goto(url, timeout=timeout)
            logger.debug(f"Tab {tab_id} navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed for tab {tab_id}: {e}")
            return False

    def refresh(self, browser_id: str, tab_id: str) -> bool:
        if tab_id in self._pages:
            self._pages[tab_id].reload()
            return True
        return False
        
    def get_url(self, browser_id: str, tab_id: str) -> str:
        if tab_id in self._pages:
            return self._pages[tab_id].url
        return ""

    def get_title(self, browser_id: str, tab_id: str) -> str:
        if tab_id in self._pages:
            return self._pages[tab_id].title()
        return ""
