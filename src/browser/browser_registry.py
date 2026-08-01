from typing import Dict, Optional, List
import threading
from src.utils.logger import get_logger
from .browser_models import BrowserInstance, BrowserSession, BrowserStatus

logger = get_logger("browser.registry")

class BrowserRegistry:
    """
    Maintains the state of running browsers.
    Hierarchy: BrowserRegistry -> BrowserInstance -> BrowserSession -> Tabs
    """
    def __init__(self):
        self._instances: Dict[str, BrowserInstance] = {}
        self._sessions: Dict[str, BrowserSession] = {}
        # Map browser instance ID to session ID
        self._instance_to_session: Dict[str, str] = {}
        self._lock = threading.Lock()

    def register_instance(self, instance: BrowserInstance) -> None:
        with self._lock:
            self._instances[instance.id] = instance
            logger.debug(f"Registered BrowserInstance: {instance.id}")

    def unregister_instance(self, browser_id: str) -> None:
        with self._lock:
            if browser_id in self._instances:
                del self._instances[browser_id]
            if browser_id in self._instance_to_session:
                session_id = self._instance_to_session[browser_id]
                if session_id in self._sessions:
                    del self._sessions[session_id]
                del self._instance_to_session[browser_id]
            logger.debug(f"Unregistered BrowserInstance: {browser_id}")

    def get_instance(self, browser_id: str) -> Optional[BrowserInstance]:
        return self._instances.get(browser_id)

    def list_instances(self) -> List[BrowserInstance]:
        return list(self._instances.values())

    def register_session(self, browser_id: str, session: BrowserSession) -> None:
        with self._lock:
            self._sessions[session.session_id] = session
            self._instance_to_session[browser_id] = session.session_id
            logger.debug(f"Registered BrowserSession {session.session_id} to instance {browser_id}")

    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        return self._sessions.get(session_id)

    def get_session_for_browser(self, browser_id: str) -> Optional[BrowserSession]:
        session_id = self._instance_to_session.get(browser_id)
        if session_id:
            return self._sessions.get(session_id)
        return None
