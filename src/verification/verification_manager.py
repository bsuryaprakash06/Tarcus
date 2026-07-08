from typing import Dict, List, Any
from src.models.target import TargetSession
from src.models.verification import VerificationStatus, VerificationResult, ToolMetadata
from src.events.pipeline_events import PipelineEventBus
from src.verification.verification_provider import VerificationProvider
from src.verification.verification_cache import VerificationCache
from src.verification.verification_pipeline import VerificationPipeline
from src.verification.verification_events import (
    VerificationStarted,
    VerificationCompleted,
    VerificationFailed,
    VerificationSkipped,
    VerificationPartial
)
from src.utils.logger import get_logger

logger = get_logger("verification.manager")

class VerificationManager:
    """
    Orchestrates the verification process by mapping ToolMetadata to the VerificationPipeline.
    """
    def __init__(self, provider: VerificationProvider):
        self.provider = provider
        self.cache = VerificationCache(ttl_seconds=0.5)
        self.pipeline = VerificationPipeline(self.provider, self.cache)
        self.event_bus = PipelineEventBus()

    def verify(self, step_id: str, metadata: ToolMetadata, session: TargetSession, context: Dict[str, Any] = None) -> VerificationResult:
        if not metadata.verification_rules:
            logger.debug(f"[{step_id}] No verification rules for tool '{metadata.tool_name}'. Skipping.")
            self.event_bus.publish_event(VerificationSkipped(
                step_id=step_id,
                target_id=session.target.id,
                reason="No rules defined in metadata."
            ))
            return VerificationResult(status=VerificationStatus.SUCCESS)

        self.event_bus.publish_event(VerificationStarted(
            step_id=step_id,
            target_id=session.target.id,
            tool_name=metadata.tool_name,
            rules=metadata.verification_rules
        ))

        # Execute the pipeline
        result = self.pipeline.execute(metadata.verification_rules, session, context)

        # Publish appropriate event based on result
        if result.status == VerificationStatus.SUCCESS:
            self.event_bus.publish_event(VerificationCompleted(
                step_id=step_id,
                target_id=session.target.id,
                result=result
            ))
        elif result.status == VerificationStatus.PARTIAL:
            self.event_bus.publish_event(VerificationPartial(
                step_id=step_id,
                target_id=session.target.id,
                result=result
            ))
        else:
            self.event_bus.publish_event(VerificationFailed(
                step_id=step_id,
                target_id=session.target.id,
                result=result
            ))

        return result
