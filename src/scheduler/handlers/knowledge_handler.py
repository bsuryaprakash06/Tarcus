from typing import Any
from src.scheduler.handlers.base_handler import BaseHandler
from src.models.scheduler import ExecutionNode
from src.utils.logger import get_logger

logger = get_logger("scheduler.handlers.knowledge")

class KnowledgeHandler(BaseHandler):
    """
    Executes an LLM knowledge lookup.
    """
    def __init__(self):
        from src.services.llm_chat_service import LLMChatService
        self.chat_service = LLMChatService()

    def execute(self, node: ExecutionNode) -> Any:
        # node.payload is expected to be a dictionary: {"text": "explain RAM", "history_str": "..."}
        payload = node.payload
        if not isinstance(payload, dict) or "text" not in payload:
            raise ValueError("KnowledgeHandler payload must be a dict with 'text'.")
            
        text = payload["text"]
        history = payload.get("history_str", "")
        
        logger.info(f"KnowledgeHandler generating response for: '{text}'")
        
        # We can dynamically configure profiles or streaming later.
        from src.models.profile import ResponseProfile, ResponseMode
        profile = ResponseProfile(mode=ResponseMode.KNOWLEDGE, max_sentences=3, ask_followup=False)
        
        response = self.chat_service.respond(text, profile, history)
        return response
