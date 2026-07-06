from typing import Tuple
from src.context.session import SessionStore
from src.context.context_resolver import ContextResolver
from src.context.entity_tracker import EntityTracker
from src.models.context import SessionContext
from src.models.plan import ExecutionPlan

class ContextManager:
    """Facade orchestrating context resolution, entity tracking, and session lifecycle."""
    
    def __init__(self):
        self.session_store = SessionStore()
        self.resolver = ContextResolver()
        self.tracker = EntityTracker()
        
    def resolve_reference(self, text: str) -> Tuple[str, float]:
        """Resolves references and updates last_activity."""
        session = self.session_store.get_or_create_session()
        session.touch()
        return self.resolver.resolve(text, session)
        
    def extract_from_plan(self, plan: ExecutionPlan) -> None:
        """Tracks entities from a planner payload."""
        session = self.session_store.get_or_create_session()
        session.touch()
        self.tracker.extract_from_plan(plan, session)
        
    def extract_knowledge_topic(self, query: str) -> None:
        """Tracks topics from a knowledge interaction."""
        session = self.session_store.get_or_create_session()
        session.touch()
        self.tracker.extract_knowledge_topic(query, session)
        
    def get_session(self) -> SessionContext:
        """Retrieves the active session."""
        return self.session_store.get_or_create_session()
        
    def clear_session(self) -> None:
        """Explicitly wipes all conversational context."""
        self.session_store.clear_session()
