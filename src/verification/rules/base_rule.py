from abc import ABC, abstractmethod
from typing import Dict, Any
from src.models.target import TargetSession
from src.verification.verification_provider import VerificationProvider

class BaseVerificationRule(ABC):
    """
    Abstract base class for all verification rules.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def evaluate(self, session: TargetSession, context: Dict[str, Any], provider: VerificationProvider) -> bool:
        """
        Evaluates the specific rule condition. 
        Returns True if the verification passes.
        """
        pass
