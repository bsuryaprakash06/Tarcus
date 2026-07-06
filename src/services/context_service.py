from typing import Tuple
from src.context.context_manager import ContextManager
from src.models.plan import ExecutionPlan
from src.utils.settings import ENABLE_CONTEXT_MANAGER

class ContextService:
    """Public interface for conversational context orchestration."""
    
    def __init__(self):
        self.manager = ContextManager()
        
    def resolve_reference(self, text: str) -> Tuple[str, float]:
        """
        Attempts to resolve context references (pronouns).
        Returns the resolved text and a confidence score (0.0 to 1.0).
        """
        if not ENABLE_CONTEXT_MANAGER:
            return text, 1.0
        return self.manager.resolve_reference(text)
        
    def track_execution_plan(self, plan: ExecutionPlan) -> None:
        """Extracts automation entities from a generated execution plan."""
        if ENABLE_CONTEXT_MANAGER:
            self.manager.extract_from_plan(plan)
            
    def track_knowledge_query(self, query: str) -> None:
        """Extracts the topic from a knowledge query."""
        if ENABLE_CONTEXT_MANAGER:
            self.manager.extract_knowledge_topic(query)
            
    def clear_session(self) -> None:
        """Forces the current session context to be completely wiped."""
        if ENABLE_CONTEXT_MANAGER:
            self.manager.clear_session()
