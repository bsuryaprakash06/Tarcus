from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"

class RecoveryStatus(str, Enum):
    NONE = "NONE"
    RECOVERING = "RECOVERING"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"

class RecoveryStrategy(str, Enum):
    REFRESH_TARGET = "REFRESH_TARGET"
    REFOCUS = "REFOCUS"
    REDISCOVER = "REDISCOVER"
    RETRY = "RETRY"
    FALLBACK = "FALLBACK"
    ABORT = "ABORT"

class RecoveryPolicy(BaseModel):
    """Governs how the Recovery Engine should attempt to recover a failed verification."""
    strategies: List[RecoveryStrategy] = Field(
        default=[
            RecoveryStrategy.REFOCUS,
            RecoveryStrategy.REDISCOVER,
            RecoveryStrategy.RETRY
        ]
    )
    max_retries: int = 2

class VerificationResult(BaseModel):
    """A rich result object returned by the Verification Pipeline."""
    status: VerificationStatus
    confidence: float = 1.0
    details: str = ""
    failed_rules: List[str] = Field(default_factory=list)
    elapsed_ms: float = 0.0
    recommendation: Optional[RecoveryStrategy] = None

class ToolMetadata(BaseModel):
    """
    Metadata attached to a BaseTool that governs its automated lifecycle.
    Keeps tools 'dumb' while informing the ExecutionController how to verify and recover.
    """
    tool_name: str
    verification_rules: List[str] = Field(default_factory=list) # e.g. ["window_exists", "process_running"]
    recovery_policy: RecoveryPolicy = Field(default_factory=RecoveryPolicy)
    timeout_sec: float = 10.0
