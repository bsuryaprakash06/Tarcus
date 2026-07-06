from typing import Tuple, Optional
from src.utils.logger import get_logger
from src.services.context_service import ContextService
from src.models.dialogue_state import ConversationState, DialogueState, PendingClarification, PendingConfirmation
from src.dialogue.merge_engine import HybridMergeEngine

logger = get_logger("dialogue.manager")

class DialogueManager:
    """Master orchestrator separating memory (Context) from conversational flow (State)."""
    
    def __init__(self):
        self.context_service = ContextService()
        self.conversation_state = ConversationState()
        self.merge_engine = HybridMergeEngine()
        
    def set_pending_clarification(self, original_text: str, intent: str, reason: str):
        """Suspends an ambiguous request awaiting user reply."""
        self.conversation_state.dialogue_state = DialogueState.WAITING_FOR_CLARIFICATION
        self.conversation_state.pending_clarification = PendingClarification(
            original_text=original_text,
            intent=intent,
            reason=reason
        )
        logger.info(f"Pending Clarification created for: '{original_text}'")
        
    def get_pending_clarification(self) -> Optional[PendingClarification]:
        """Returns the pending clarification if valid and not expired."""
        pending = self.conversation_state.pending_clarification
        if pending:
            if pending.is_expired:
                logger.info(f"Pending Clarification expired.")
                self.clear_pending_clarification()
                return None
            return pending
        return None
        
    def increment_clarification_attempt(self):
        pending = self.conversation_state.pending_clarification
        if pending:
            pending.attempts += 1
            if pending.attempts > pending.max_attempts:
                logger.info("Max clarification attempts reached. Cancelling.")
                self.clear_pending_clarification()
                return True # Indicates it was cancelled
        return False
                
    def clear_pending_clarification(self):
        self.conversation_state.pending_clarification = None
        self.conversation_state.dialogue_state = DialogueState.IDLE
        
    def set_pending_confirmation(self, plan, reason: str):
        self.conversation_state.dialogue_state = DialogueState.WAITING_FOR_CONFIRMATION
        self.conversation_state.pending_confirmation = PendingConfirmation(
            plan=plan,
            reason=reason
        )
        logger.info(f"Pending Confirmation created for destructive action.")
        
    def get_pending_confirmation(self):
        pending = self.conversation_state.pending_confirmation
        if pending:
            if pending.is_expired:
                logger.info(f"Pending Confirmation expired.")
                self.clear_pending_confirmation()
                return None
            return pending
        return None
        
    def clear_pending_confirmation(self):
        self.conversation_state.pending_confirmation = None
        self.conversation_state.dialogue_state = DialogueState.IDLE
        
    def merge_clarification(self, original_text: str, reply_text: str) -> str:
        """Merges a user's reply into the suspended request."""
        return self.merge_engine.merge(original_text, reply_text)
        
    def check_cancellation(self, text: str) -> bool:
        """Detects if user is abandoning the current dialogue flow."""
        cancel_phrases = {"nevermind", "never mind", "cancel", "stop", "forget it", "doesn't matter", "abort"}
        clean_text = text.lower().strip('.!?')
        return clean_text in cancel_phrases
        
    def add_to_history(self, role: str, content: str):
        history = self.conversation_state.conversation_history
        history.append({"role": role, "content": content})
        if len(history) > 10:
            history.pop(0)
            
    def get_history_string(self) -> str:
        history = self.conversation_state.conversation_history
        if not history:
            return ""
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
        
    # Proxies to ContextService
    def resolve_reference(self, text: str, intent: str) -> Tuple[str, float]:
        return self.context_service.resolve_reference(text, intent)
        
    def clear_session(self):
        self.context_service.clear_session()
        self.clear_pending_clarification()
