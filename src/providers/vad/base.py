from abc import ABC, abstractmethod
import numpy as np

class BaseVADProvider(ABC):
    """Base interface for Voice Activity Detection."""
    
    @abstractmethod
    def process_frame(self, frame: np.ndarray) -> bool:
        """Process an audio frame and return True if speech is detected."""
        pass
        
    @abstractmethod
    def reset(self) -> None:
        """Reset internal state."""
        pass
