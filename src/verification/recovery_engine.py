from typing import List, Dict, Any, Callable
from src.models.target import TargetSession
from src.models.verification import RecoveryPolicy, RecoveryStrategy, RecoveryStatus
from src.events.pipeline_events import PipelineEventBus
from src.verification.verification_events import RecoveryStarted, RecoverySucceeded, RecoveryFailed
from src.utils.logger import get_logger

logger = get_logger("verification.recovery")

class RecoveryEngine:
    """
    Executes a chain of recovery strategies when verification fails.
    Does not require tools to know how to recover themselves.
    """
    def __init__(self, backend):
        self.backend = backend
        self.event_bus = PipelineEventBus()

    def attempt_recovery(self, step_id: str, session: TargetSession, policy: RecoveryPolicy) -> RecoveryStatus:
        if not policy.strategies:
            return RecoveryStatus.FAILED

        self.event_bus.publish_event(RecoveryStarted(
            step_id=step_id,
            target_id=session.target.id,
            reason="Verification Failed"
        ))

        for strategy in policy.strategies:
            logger.info(f"Attempting recovery strategy: {strategy.value} for step {step_id}")
            success = self._execute_strategy(strategy, session)
            
            if success:
                self.event_bus.publish_event(RecoverySucceeded(
                    step_id=step_id,
                    target_id=session.target.id,
                    strategy=strategy.value
                ))
                return RecoveryStatus.RECOVERED

        self.event_bus.publish_event(RecoveryFailed(
            step_id=step_id,
            target_id=session.target.id,
            strategy="ALL",
            error="All recovery strategies exhausted."
        ))
        return RecoveryStatus.FAILED

    def _execute_strategy(self, strategy: RecoveryStrategy, session: TargetSession) -> bool:
        try:
            if strategy == RecoveryStrategy.REFOCUS:
                return self.backend.focus(session)
            elif strategy == RecoveryStrategy.REDISCOVER:
                # Requires interaction manager to resync graph
                # For now, we simulate success if backend resolve works
                return self.backend.resolve(session, session.target.properties.get("name", "")) is not None
            elif strategy == RecoveryStrategy.RETRY:
                # This just means the recovery engine has cleared the way for a retry
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error executing recovery strategy {strategy.value}: {e}")
            return False
