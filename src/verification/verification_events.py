from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime
from src.models.verification import VerificationStatus, RecoveryStatus, VerificationResult

class VerificationEvent(BaseModel):
    timestamp: datetime = datetime.utcnow()
    step_id: str
    target_id: str

# Verification Pipeline Events
class VerificationStarted(VerificationEvent):
    tool_name: str
    rules: List[str]

class VerificationSkipped(VerificationEvent):
    reason: str

class VerificationPartial(VerificationEvent):
    result: VerificationResult

class VerificationCompleted(VerificationEvent):
    result: VerificationResult

class VerificationFailed(VerificationEvent):
    result: VerificationResult

# Recovery Engine Events
class RecoveryStarted(VerificationEvent):
    reason: str

class RecoverySucceeded(VerificationEvent):
    strategy: str

class RecoveryFailed(VerificationEvent):
    strategy: str
    error: str

# Retry Events
class RetryStarted(VerificationEvent):
    attempt: int
    max_attempts: int

class RetryFinished(VerificationEvent):
    attempt: int
    success: bool
