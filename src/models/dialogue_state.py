from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class DialogueState(str, Enum):
    IDLE = "IDLE"
    WAITING_FOR_CONFIRMATION = "WAITING_FOR_CONFIRMATION"
    WAITING_FOR_CLARIFICATION = "WAITING_FOR_CLARIFICATION"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"
    PROCESSING = "PROCESSING"
    RESPONDING = "RESPONDING"

class PendingClarification(BaseModel):
    original_text: str
    intent: str
    reason: str
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    expires_at: float = Field(default_factory=lambda: datetime.now().timestamp() + 300.0) # 5 min default
    attempts: int = 1
    max_attempts: int = 3
    
    @property
    def is_expired(self) -> bool:
        return datetime.now().timestamp() > self.expires_at

class PendingConfirmation(BaseModel):
    plan: Any
    reason: str
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    expires_at: float = Field(default_factory=lambda: datetime.now().timestamp() + 300.0) # 5 min default
    
    @property
    def is_expired(self) -> bool:
        return datetime.now().timestamp() > self.expires_at

class ConversationState(BaseModel):
    dialogue_state: DialogueState = DialogueState.IDLE
    pending_clarification: Optional[PendingClarification] = None
    pending_confirmation: Optional[PendingConfirmation] = None
    last_system_prompt: Optional[str] = None
    last_user_reply: Optional[str] = None
    conversation_history: list = Field(default_factory=list)
