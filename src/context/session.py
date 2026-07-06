import uuid
from datetime import datetime
from typing import Optional
from src.models.context import SessionContext
from src.utils.settings import CONTEXT_TIMEOUT_MINUTES
from src.utils.logger import get_logger

logger = get_logger("context.session")

class SessionStore:
    """In-memory singleton storage for the current SessionContext."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionStore, cls).__new__(cls)
            cls._instance.current_session = None
        return cls._instance
        
    def get_or_create_session(self) -> SessionContext:
        """Retrieves the active session, or creates a new one if it expired or doesn't exist."""
        now = datetime.now().timestamp()
        
        # Check for 10-minute inactivity expiration
        if self.current_session:
            timeout_seconds = CONTEXT_TIMEOUT_MINUTES * 60
            if (now - self.current_session.last_activity) > timeout_seconds:
                logger.info(f"Session expired after {CONTEXT_TIMEOUT_MINUTES} minutes of inactivity. Clearing context.")
                self.clear_session()
                
        if not self.current_session:
            self.current_session = SessionContext(session_id=str(uuid.uuid4()))
            logger.debug(f"Created new SessionContext: {self.current_session.session_id}")
            
        return self.current_session
        
    def clear_session(self) -> None:
        """Forces the current session to expire and clear."""
        if self.current_session:
            logger.debug(f"Explicitly clearing session {self.current_session.session_id}")
        self.current_session = None
