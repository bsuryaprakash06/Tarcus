import time
from typing import List, Dict, Any, Type
from src.models.target import TargetSession
from src.models.verification import VerificationStatus, VerificationResult
from src.verification.verification_provider import VerificationProvider
from src.verification.verification_cache import VerificationCache
from src.utils.logger import get_logger

logger = get_logger("verification.pipeline")

class VerificationPipeline:
    """
    Chains multiple verification rules together.
    All rules must pass for the pipeline to declare SUCCESS.
    """
    def __init__(self, provider: VerificationProvider, cache: VerificationCache):
        self.provider = provider
        self.cache = cache

    def execute(self, rules: List[str], session: TargetSession, context: Dict[str, Any] = None) -> VerificationResult:
        """
        Executes a sequence of rules in order.
        """
        if not rules:
            return VerificationResult(
                status=VerificationStatus.SUCCESS,
                details="No verification rules required."
            )
            
        start_time = time.time()
        context = context or {}
        failed_rules = []
        
        for rule_name in rules:
            # Check Cache
            cached_result = self.cache.get(session.target.id, rule_name)
            if cached_result is not None:
                passed = cached_result
                logger.debug(f"Rule {rule_name} resolved from cache: {passed}")
            else:
                try:
                    passed = self.provider.evaluate(rule_name, session, context)
                    self.cache.set(session.target.id, rule_name, passed)
                except Exception as e:
                    logger.error(f"Error evaluating verification rule '{rule_name}': {e}")
                    passed = False
            
            if not passed:
                failed_rules.append(rule_name)

        elapsed = (time.time() - start_time) * 1000.0

        if not failed_rules:
            return VerificationResult(
                status=VerificationStatus.SUCCESS,
                elapsed_ms=elapsed,
                details="All verification rules passed."
            )
        else:
            return VerificationResult(
                status=VerificationStatus.FAILED if len(failed_rules) == len(rules) else VerificationStatus.PARTIAL,
                failed_rules=failed_rules,
                elapsed_ms=elapsed,
                details=f"Verification failed on rules: {', '.join(failed_rules)}"
            )
