from abc import ABC, abstractmethod
from typing import Generator, Iterable

class BaseSTTProvider(ABC):
    """
    Base interface for Speech-to-Text providers.
    Supports both batch transcription and future streaming transcription.
    """
    
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe a complete audio buffer."""
        pass
        
    @abstractmethod
    def stream(self, audio_chunks: Iterable[bytes]) -> Generator[str, None, None]:
        """Stream chunks of audio and yield partial/final transcripts."""
        pass
        
    @abstractmethod
    def reset(self) -> None:
        """Reset the streaming state."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop processing immediately."""
        pass
