import time
import requests
from .base import BaseProvider, ProviderResponse
from src.utils.settings import MODEL_NAME, GROQ_API_KEY, API_KEY, BASE_URL
from src.utils.logger import get_logger

logger = get_logger("providers.groq")

class GroqProvider(BaseProvider):
    """Groq backend provider integration."""

    def __init__(self):
        self.model_name = MODEL_NAME or "llama-3.3-70b-versatile"
        self.base_url = BASE_URL or "https://api.groq.com/openai/v1/chat/completions"
        if not self.base_url.endswith("/chat/completions"):
            self.base_url = self.base_url.rstrip("/") + "/chat/completions"
        self.api_key = GROQ_API_KEY or API_KEY

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def supports_json_mode(self) -> bool:
        return True

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def supports_vision(self) -> bool:
        return False

    @property
    def supports_tool_calling(self) -> bool:
        return True

    def generate(self, system_prompt: str, user_prompt: str, require_json: bool = False) -> ProviderResponse:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0
        }
        
        if require_json:
            payload["response_format"] = {"type": "json_object"}

        logger.info(f"Sending request to Groq ({self.model_name}) at {self.base_url}...")
        start_time = time.time()
        
        response = requests.post(self.base_url, json=payload, headers=headers, timeout=60)
        latency = time.time() - start_time
        
        if response.status_code != 200:
            logger.error(f"Groq returned HTTP {response.status_code}: {response.text}")
            response.raise_for_status()

        result_json = response.json()
        choices = result_json.get("choices", [])
        if not choices:
            raw_text = ""
        else:
            raw_text = choices[0].get("message", {}).get("content", "")

        raw_usage = result_json.get("usage", {})
        usage = {
            "prompt_tokens": raw_usage.get("prompt_tokens", 0),
            "completion_tokens": raw_usage.get("completion_tokens", 0),
            "total_tokens": raw_usage.get("total_tokens", 0)
        }

        return ProviderResponse(
            text=raw_text,
            model_name=self.model_name,
            provider_name=self.provider_name,
            latency=latency,
            usage=usage
        )
