from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InputSource(str, Enum):
    VOICE = "VOICE"
    TEXT = "TEXT"
    API = "API"
    PLUGIN = "PLUGIN"

class InputRequest(BaseModel):
    """The unified data structure representing a user request from any source."""
    request_id: str
    source: InputSource
    text: str
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"

class MessageStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class ConversationMessage(BaseModel):
    """Represents a rich message in the UI conversation history."""
    message_id: str
    role: MessageRole
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    source: Optional[InputSource] = None
    status: MessageStatus = MessageStatus.PENDING
    workflow_id: Optional[str] = None
    content: str
