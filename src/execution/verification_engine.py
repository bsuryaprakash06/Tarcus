from typing import Dict, Any, Tuple
from abc import ABC, abstractmethod
from src.models.workflow_execution import VerificationRule
from src.models.target import VerificationResult, TargetSession
from src.utils.logger import get_logger
import time

logger = get_logger("execution.verification_engine")

class VerificationStrategy(ABC):
    @abstractmethod
    def verify(self, rule: VerificationRule, context: Any) -> Tuple[VerificationResult, str]:
        pass

class OpenApplicationVerifier(VerificationStrategy):
    def verify(self, rule: VerificationRule, context: Any) -> Tuple[VerificationResult, str]:
        # A more advanced verification would query the OS or InteractionManager for the new window.
        return VerificationResult.SUCCESS, ""

class TypeTextVerifier(VerificationStrategy):
    def verify(self, rule: VerificationRule, context: Any) -> Tuple[VerificationResult, str]:
        # A more advanced verification would read the text back from the control and return PARTIAL if only some typed.
        return VerificationResult.SUCCESS, ""

class VerificationEngine:
    """Strategy-based postcondition verification using VerificationResult."""
    def __init__(self):
        self.strategies: Dict[str, VerificationStrategy] = {
            "OpenApplicationVerifier": OpenApplicationVerifier(),
            "TypeTextVerifier": TypeTextVerifier(),
        }
        
    def register_strategy(self, name: str, strategy: VerificationStrategy):
        self.strategies[name] = strategy
        
    def verify(self, rule: VerificationRule, context: Any) -> Tuple[VerificationResult, str]:
        strategy = self.strategies.get(rule.strategy)
        if not strategy:
            return VerificationResult.FAILED, f"Verification strategy '{rule.strategy}' not found."
            
        try:
            return strategy.verify(rule, context)
        except Exception as e:
            logger.error(f"Verification strategy {rule.strategy} crashed: {e}")
            return VerificationResult.FAILED, f"Verification crashed: {e}"
