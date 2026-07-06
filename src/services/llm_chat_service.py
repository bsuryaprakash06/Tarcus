import json
from pydantic import BaseModel
from typing import List, Optional
from src.providers import get_provider_from_settings
from src.utils.logger import get_logger
from src.models.response import ResponseProfile

logger = get_logger("services.llm_chat")

class KnowledgeResponse(BaseModel):
    answer: str
    primary_topic: Optional[str] = None
    secondary_topics: List[str] = []

CHAT_SYSTEM_PROMPT = """You are Tarcus, a highly intelligent and helpful AI assistant.
Answer the user's questions clearly, accurately, and without markdown formatting.
Your response will be spoken aloud by a Text-to-Speech engine, so keep it conversational and easy to listen to.
IMPORTANT: You MUST return your response as a valid JSON object matching this schema:
{
    "answer": "The spoken answer text.",
    "primary_topic": "The main topic being discussed (1-3 words)",
    "secondary_topics": ["topic1", "topic2"]
}
"""

class LLMChatService:
    """
    Handles general LLM requests (knowledge, summarizing, writing) that don't involve
    executing tools on the local machine.
    """
    def __init__(self):
        self.provider = get_provider_from_settings()
        
    def respond(self, text: str, profile: ResponseProfile = None, history_str: str = "") -> KnowledgeResponse:
        
        dynamic_prompt = CHAT_SYSTEM_PROMPT
        if history_str:
            dynamic_prompt += f"\n\nCONVERSATION HISTORY:\n{history_str}\n\nUse the history above to understand the context of the user's latest request.\n"
            
        if profile:
            dynamic_prompt += f"\nCRITICAL RULES:\n"
            dynamic_prompt += f"1. Your answer must be at most {profile.max_sentences} short sentences.\n"
            dynamic_prompt += f"2. Adopt a {profile.style} style.\n"
            if profile.ask_followup:
                dynamic_prompt += f"3. End by asking if the user wants more detail when appropriate.\n"
        
        try:
            response = self.provider.generate(system_prompt=dynamic_prompt, user_prompt=text, require_json=True)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3]
                
            parsed = json.loads(raw_text.strip())
            return KnowledgeResponse(
                answer=parsed.get("answer", "I'm not sure."),
                primary_topic=parsed.get("primary_topic"),
                secondary_topics=parsed.get("secondary_topics", [])
            )
        except Exception as e:
            logger.error(f"LLMChatService execution failed: {e}")
            return KnowledgeResponse(answer="I'm sorry, I'm having trouble connecting to my brain right now.")
