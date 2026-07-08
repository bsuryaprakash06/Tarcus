from typing import Dict, Any
from src.models.target import TargetSession
from src.verification.verification_provider import VerificationProvider
from src.verification.rules.base_rule import BaseVerificationRule

class ControlExistsRule(BaseVerificationRule):
    @property
    def name(self) -> str:
        return "control_exists"
        
    def evaluate(self, session: TargetSession, context: Dict[str, Any], provider: VerificationProvider) -> bool:
        return provider.evaluate(self.name, session, context)
