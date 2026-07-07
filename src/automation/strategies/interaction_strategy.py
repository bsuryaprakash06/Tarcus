from abc import ABC, abstractmethod
from typing import Any
from src.models.target import TargetSession

class InteractionStrategy(ABC):
    """
    Base interface for specific interaction strategies.
    Different backends can implement their own specific strategies for the same action.
    """
    @abstractmethod
    def execute(self, session: TargetSession, **kwargs) -> bool:
        pass
