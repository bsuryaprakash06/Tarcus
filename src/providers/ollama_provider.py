import time
import requests
from src.providers.base_provider import BaseProvider, ProviderResponse
from src.utils.settings import MODEL_NAME, BASE_URL
from src.utils.logger import get_logger

logger = get_logger("providers.ollama")

class OllamaProvider(BaseProvider):
    """Ollama backend provider integration."""

    def __init__(self):
        self.model_name = MODEL_NAME or "qwen3:4b"
        self.base_url = BASE_URL or "http://localhost:11434/api/chat"
        # If user passed only the host, construct the chat endpoint
        if "/api/chat" not in self.base_url and "/v1" not in self.base_url:
            # Strip trailing slash if present
            self.base_url = self.base_url.rstrip("/") + "/api/chat"

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def supports_json_mode(self) -> bool:
        return False

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def supports_vision(self) -> bool:
        return False

    @property
    def supports_tool_calling(self) -> bool:
        return False

    def generate(self, system_prompt: str, user_prompt: str) -> ProviderResponse:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.0,
                "thinking": False
            },
            "think": False
        }

        logger.info(f"Sending request to Ollama ({self.model_name}) at {self.base_url}...")
        start_time = time.time()
        
        # Increase timeout to 90 seconds to allow for initial model loading
        response = requests.post(self.base_url, json=payload, timeout=90)
        latency = time.time() - start_time
        
        if response.status_code != 200:
            logger.error(f"Ollama returned HTTP {response.status_code}: {response.text}")
            response.raise_for_status()

        result_json = response.json()
        raw_text = result_json.get("message", {}).get("content", "")
        
        # Capture optional token metrics if supplied by Ollama
        usage = {
            "prompt_tokens": result_json.get("prompt_eval_count", 0),
            "completion_tokens": result_json.get("eval_count", 0),
            "total_tokens": result_json.get("prompt_eval_count", 0) + result_json.get("eval_count", 0)
        }

        return ProviderResponse(
            text=raw_text,
            model_name=self.model_name,
            provider_name=self.provider_name,
            latency=latency,
            usage=usage
        )
