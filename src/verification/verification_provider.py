from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.models.target import TargetSession

class VerificationProvider(ABC):
    """
    Abstract interface for platform-specific verification checks.
    Similar to AutomationBackend, but dedicated to stateless read/verify operations.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
        
    @abstractmethod
    def evaluate(self, rule_name: str, session: TargetSession, context: Dict[str, Any]) -> bool:
        """
        Evaluates a specific rule (e.g. 'window_exists') against the target session.
        Returns True if the condition is met.
        """
        pass
