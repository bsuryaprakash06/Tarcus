from abc import ABC, abstractmethod
from typing import Generator, Iterable

class BaseTTSProvider(ABC):
    """
    Base interface for Text-to-Speech providers.
    Supports both batch synthesis and future streaming synthesis.
    """
    
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Synthesize a complete string of text into an audio buffer (e.g. WAV or PCM bytes)."""
        pass
        
    @abstractmethod
    def stream(self, text_chunks: Iterable[str]) -> Generator[bytes, None, None]:
        """Stream chunks of text and yield audio buffers."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop processing immediately."""
        pass
