from .base import BaseVADProvider
from .silero_provider import SileroVADProvider
from src.providers.registry import ProviderRegistry

ProviderRegistry.register("vad", "silero", SileroVADProvider)

__all__ = [
    "BaseVADProvider",
    "SileroVADProvider"
]
