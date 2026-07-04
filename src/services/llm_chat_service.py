from src.providers import get_provider_from_settings
from src.utils.logger import get_logger
from src.models.response import ResponseProfile

logger = get_logger("services.llm_chat")

CHAT_SYSTEM_PROMPT = """You are Tarcus, a highly intelligent and helpful AI assistant.
Answer the user's questions clearly, accurately, and without markdown formatting.
Your response will be spoken aloud by a Text-to-Speech engine, so keep it conversational and easy to listen to.
"""

class LLMChatService:
    """
    Handles general LLM requests (knowledge, summarizing, writing) that don't involve
    executing tools on the local machine.
    """
    def __init__(self):
        self.provider = get_provider_from_settings()
        
    def respond(self, text: str, profile: ResponseProfile = None) -> str:
        
        dynamic_prompt = CHAT_SYSTEM_PROMPT
        if profile:
            dynamic_prompt += f"\nCRITICAL RULES:\n"
            dynamic_prompt += f"1. Your answer must be at most {profile.max_sentences} short sentences.\n"
            dynamic_prompt += f"2. Adopt a {profile.style} style.\n"
            if profile.ask_followup:
                dynamic_prompt += f"3. End by asking if the user wants more detail when appropriate.\n"
        
        try:
            response = self.provider.generate(system_prompt=dynamic_prompt, user_prompt=text, require_json=False)
            return response.text.strip()
        except Exception as e:
            logger.error(f"LLMChatService execution failed: {e}")
            return "I'm sorry, I'm having trouble connecting to my brain right now."
