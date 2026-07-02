from .base_provider import BaseProvider, ProviderResponse
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .groq_provider import GroqProvider
from src.utils.settings import LLM_PROVIDER

# Provider registry mapping provider identifiers to their respective classes
_PROVIDER_REGISTRY = {}

def register_provider(provider_id: str, provider_class) -> None:
    """
    Registers a provider class under a given unique identifier.
    
    Args:
        provider_id: Unique string identifier of the provider.
        provider_class: Class of the provider (subclass of BaseProvider).
    """
    _PROVIDER_REGISTRY[provider_id.lower().strip()] = provider_class

# Auto-register core provider integrations
register_provider("ollama", OllamaProvider)
register_provider("openai", OpenAIProvider)
register_provider("groq", GroqProvider)

def get_provider_from_settings() -> BaseProvider:
    """
    Instantiates and returns the provider configured in settings.
    
    Returns:
        BaseProvider: An instance of the configured provider.
        
    Raises:
        ValueError: If the configured provider identifier is not registered.
    """
    provider_id = LLM_PROVIDER.lower().strip()
    provider_class = _PROVIDER_REGISTRY.get(provider_id)
    if not provider_class:
        supported = ", ".join(f"'{p}'" for p in _PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"LLM_PROVIDER '{LLM_PROVIDER}' is not registered. "
            f"Supported providers: {supported}"
        )
    return provider_class()

__all__ = [
    "BaseProvider",
    "ProviderResponse",
    "OllamaProvider",
    "OpenAIProvider",
    "GroqProvider",
    "register_provider",
    "get_provider_from_settings"
]
