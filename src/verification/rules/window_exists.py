from typing import Dict, Any
from src.models.target import TargetSession
from src.verification.verification_provider import VerificationProvider
from src.verification.rules.base_rule import BaseVerificationRule

class WindowExistsRule(BaseVerificationRule):
    @property
    def name(self) -> str:
        return "window_exists"
        
    def evaluate(self, session: TargetSession, context: Dict[str, Any], provider: VerificationProvider) -> bool:
        # Ask the provider to check if the window natively exists
        return provider.evaluate(self.name, session, context)
