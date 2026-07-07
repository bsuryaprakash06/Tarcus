import json
from pydantic import ValidationError
from src.providers import get_provider_from_settings
from src.routing.intent import Intent
from src.models.intent_result import IntentResult
from src.utils.logger import get_logger

logger = get_logger("intent_classifier")

CLASSIFIER_PROMPT = """You are the central Intent Classification engine for a voice assistant.
Your sole responsibility is to classify the user's spoken command into EXACTLY ONE of the following intents:

AUTOMATION - Interacting with the computer, system commands, opening apps, typing, clicking, executing local tools. CRITICAL: Any command containing "type", "write", or "enter" (e.g., "Type Hello Shane") is purely AUTOMATION!
LLM_CHAT - General knowledge questions, answering facts, explanations, asking for code, writing emails, summarizing.
CONVERSATION - Simple conversational greetings or pleasantries (e.g. "Hello", "Hi", "Good morning", "Thanks", "Bye"). NEVER classify a command to "type" something as CONVERSATION.
MIXED - Requests that ask the LLM to BOTH perform an action AND explain/chat about something.
UNKNOWN - Unintelligible or completely unsupported requests.

You must respond ONLY with a raw JSON object matching this schema:
{{
    "intent": "AUTOMATION|LLM_CHAT|CONVERSATION|MIXED|UNKNOWN",
    "confidence": 0.95,
    "reason": "Brief explanation of why"
}}

CRITICAL RULES:
1. Do NOT include markdown blocks (```json).
2. Do NOT include any other text or reasoning outside the JSON.
3. Your output must be parseable by Python's json.loads().
"""

class IntentClassifier:
    """
    Leverages the LLM Provider layer to classify normalized text into an IntentResult.
    Includes automated retries on schema mismatches to guarantee pipeline stability.
    """
    def __init__(self):
        # Bind to the agnostic provider configured in settings
        self.provider = get_provider_from_settings()
        
    def classify(self, text: str, max_retries: int = 2) -> IntentResult:
        for attempt in range(max_retries + 1):
            try:
                response = self.provider.generate(
                    system_prompt=CLASSIFIER_PROMPT, 
                    user_prompt=text, 
                    require_json=True
                )
                raw_text = response.text.strip()
                
                # Aggressively strip markdown code blocks if the LLM hallucinates them despite instructions
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                    
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                    
                raw_text = raw_text.strip()
                
                # Parse and validate schema
                data = json.loads(raw_text)
                result = IntentResult(**data)
                return result
                
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Intent Classification parse failure (Attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt == max_retries:
                    logger.error(f"Failed to classify intent after {max_retries} retries. Defaulting to UNKNOWN.")
                    return IntentResult(
                        intent=Intent.UNKNOWN,
                        confidence=0.0,
                        reason=f"Parse failure after retries: {str(e)}"
                    )
