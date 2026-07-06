from typing import Tuple
from src.context.context_resolver import ContextResolver
from src.context.entity_tracker import EntityTracker
from src.models.context_scope import (
    AutomationContext, KnowledgeContext, ConversationContext, 
    WorkflowContext, SystemContext
)
from src.utils.settings import ENABLE_CONTEXT_MANAGER

class ContextService:
    """Public interface for conversational context orchestration."""
    
    def __init__(self):
        self.automation_context = AutomationContext()
        self.knowledge_context = KnowledgeContext()
        self.conversation_context = ConversationContext()
        self.workflow_context = WorkflowContext()
        self.system_context = SystemContext()
        
        if ENABLE_CONTEXT_MANAGER:
            self.resolver = ContextResolver(self)
            self.tracker = EntityTracker(self)
        
    def resolve_reference(self, text: str, intent: str) -> Tuple[str, float]:
        """
        Attempts to resolve context references (pronouns).
        Returns the resolved text and a confidence score (0.0 to 1.0).
        """
        if not ENABLE_CONTEXT_MANAGER:
            return text, 1.0
        return self.resolver.resolve_reference(text, intent)
            
    def clear_session(self) -> None:
        """Forces the current session context to be completely wiped."""
        if ENABLE_CONTEXT_MANAGER:
            self.automation_context = AutomationContext()
            self.knowledge_context = KnowledgeContext()
            self.conversation_context = ConversationContext()
            self.workflow_context = WorkflowContext()
