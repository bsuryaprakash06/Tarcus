from .registry import ProviderRegistry
from src.utils.settings import LLM_PROVIDER

# LLM Providers
from .llm.base import BaseProvider, ProviderResponse
from .llm.ollama_provider import OllamaProvider
from .llm.openai_provider import OpenAIProvider
from .llm.groq_provider import GroqProvider

# Register LLM providers
ProviderRegistry.register("llm", "ollama", OllamaProvider)
ProviderRegistry.register("llm", "openai", OpenAIProvider)
ProviderRegistry.register("llm", "groq", GroqProvider)

def get_provider_from_settings() -> BaseProvider:
    """
    Instantiates and returns the LLM provider configured in settings.
    (Kept for backward compatibility with existing code)
    """
    provider_id = LLM_PROVIDER.lower().strip()
    return ProviderRegistry.create_provider("llm", provider_id)

__all__ = [
    "ProviderRegistry",
    "BaseProvider",
    "ProviderResponse",
    "OllamaProvider",
    "OpenAIProvider",
    "GroqProvider",
    "get_provider_from_settings"
]
