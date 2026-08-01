from typing import Optional, List, Dict
import threading
import uuid
import time
from src.utils.logger import get_logger
from src.events.pipeline_events import PipelineEventBus
from .browser_models import BrowserType, BrowserStatus, BrowserInstance, BrowserSession, BrowserTab, HistoryEntry, TabStatus
from .browser_registry import BrowserRegistry
from .browser_events import (
    BrowserStarted, BrowserClosed, TabCreated, TabClosed, 
    NavigationStarted, NavigationCompleted, SessionCreated, SessionDestroyed
)
# We will hardcode to playwright for now, later dynamic via ProviderRegistry
from .backends.playwright_backend import PlaywrightBackend

logger = get_logger("browser.manager")

class BrowserManager:
    """
    Lifecycle controller for browsers.
    Loads providers, launches browsers, and updates the registry and sessions.
    """
    def __init__(self, registry: BrowserRegistry):
        self.registry = registry
        self.event_bus = PipelineEventBus()
        # In the future, this would use the ProviderRegistry
        self.backend = PlaywrightBackend()
        self._lock = threading.Lock()

    def launch(self, browser_type: BrowserType = BrowserType.CHROMIUM, headless: bool = False) -> BrowserInstance:
        with self._lock:
            # 1. Launch via backend
            backend_id = self.backend.launch(browser_type, headless=headless)
            
            # 2. Create Instance
            instance = BrowserInstance(
                id=backend_id,
                browser_type=browser_type,
                status=BrowserStatus.RUNNING,
                backend=self.backend
            )
            self.registry.register_instance(instance)
            
            # 3. Create Session
            session_id = f"sess_{uuid.uuid4().hex[:8]}"
            session = BrowserSession(session_id=session_id)
            self.registry.register_session(backend_id, session)
            
            # 4. Emit Events
            self.event_bus.publish_event(BrowserStarted(browser_id=backend_id))
            self.event_bus.publish_event(SessionCreated(session_id=session_id, browser_id=backend_id))
            
            return instance

    def close(self, browser_id: str) -> None:
        with self._lock:
            instance = self.registry.get_instance(browser_id)
            if not instance: return
            
            session = self.registry.get_session_for_browser(browser_id)
            if session:
                self.event_bus.publish_event(SessionDestroyed(session_id=session.session_id))
                
            instance.status = BrowserStatus.STOPPING
            self.backend.close(browser_id)
            self.registry.unregister_instance(browser_id)
            self.event_bus.publish_event(BrowserClosed(browser_id=browser_id))

    def create_tab(self, browser_id: str, url: str = "about:blank") -> Optional[BrowserTab]:
        with self._lock:
            session = self.registry.get_session_for_browser(browser_id)
            if not session: return None
            
            # Backend creates tab
            tab_id = self.backend.create_tab(browser_id, url)
            
            tab = BrowserTab(id=tab_id, url=url, status=TabStatus.LOADING)
            session.tabs[tab_id] = tab
            session.active_tab_id = tab_id
            
            self.event_bus.publish_event(TabCreated(session_id=session.session_id, tab_id=tab_id, url=url))
            return tab

    def close_tab(self, browser_id: str, tab_id: str) -> None:
        with self._lock:
            session = self.registry.get_session_for_browser(browser_id)
            if not session: return
            
            if tab_id in session.tabs:
                session.tabs[tab_id].status = TabStatus.CLOSED
                self.backend.close_tab(browser_id, tab_id)
                del session.tabs[tab_id]
                
                if session.active_tab_id == tab_id:
                    session.active_tab_id = list(session.tabs.keys())[-1] if session.tabs else None
                    
                self.event_bus.publish_event(TabClosed(session_id=session.session_id, tab_id=tab_id))

    def navigate(self, browser_id: str, tab_id: str, url: str) -> bool:
        session = self.registry.get_session_for_browser(browser_id)
        if not session or tab_id not in session.tabs:
            return False
            
        self.event_bus.publish_event(NavigationStarted(session_id=session.session_id, tab_id=tab_id, url=url))
        
        success = self.backend.navigate(browser_id, tab_id, url)
        
        if success:
            title = self.backend.get_title(browser_id, tab_id)
            session.tabs[tab_id].url = url
            session.tabs[tab_id].title = title
            session.tabs[tab_id].status = TabStatus.READY
            
            entry = HistoryEntry(url=url, title=title, timestamp=time.time())
            session.history.append(entry)
            
        self.event_bus.publish_event(NavigationCompleted(session_id=session.session_id, tab_id=tab_id, url=url, success=success))
        return success
