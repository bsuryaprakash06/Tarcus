from typing import Type, Dict, Any, TypeVar

# Type variable for generics (can be any base provider)
T = TypeVar('T')

class ProviderRegistry:
    """
    Central registry for managing all AI providers (LLM, STT, TTS, VAD, WakeWord).
    """
    _registry: Dict[str, Dict[str, Type[Any]]] = {
        "llm": {},
        "stt": {},
        "tts": {},
        "wakeword": {},
        "vad": {}
    }

    @classmethod
    def register(cls, category: str, provider_id: str, provider_class: Type[T]) -> None:
        """Registers a provider under a specific category."""
        category = category.lower().strip()
        provider_id = provider_id.lower().strip()
        
        if category not in cls._registry:
            cls._registry[category] = {}
            
        cls._registry[category][provider_id] = provider_class

    @classmethod
    def get_provider_class(cls, category: str, provider_id: str) -> Type[T]:
        """Retrieves a provider class."""
        category = category.lower().strip()
        provider_id = provider_id.lower().strip()
        
        cat_registry = cls._registry.get(category)
        if cat_registry is None:
            raise ValueError(f"Unknown provider category: '{category}'")
            
        provider_class = cat_registry.get(provider_id)
        if not provider_class:
            supported = ", ".join(f"'{p}'" for p in cat_registry.keys())
            raise ValueError(
                f"Provider '{provider_id}' is not registered in category '{category}'. "
                f"Supported providers: {supported}"
            )
        return provider_class

    @classmethod
    def create_provider(cls, category: str, provider_id: str, *args, **kwargs) -> Any:
        """Instantiates and returns a provider."""
        provider_class = cls.get_provider_class(category, provider_id)
        return provider_class(*args, **kwargs)
