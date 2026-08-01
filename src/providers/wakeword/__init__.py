from .base import BaseWakeWordProvider, WakeDetectionResult
from .openwakeword_provider import OpenWakeWordProvider, DummyWakeWordProvider
from src.providers.registry import ProviderRegistry

ProviderRegistry.register("wakeword", "openwakeword", OpenWakeWordProvider)
ProviderRegistry.register("wakeword", "dummy", DummyWakeWordProvider)

__all__ = [
    "BaseWakeWordProvider",
    "WakeDetectionResult",
    "OpenWakeWordProvider",
    "DummyWakeWordProvider"
]
