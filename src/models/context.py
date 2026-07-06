from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class EntityType(str, Enum):
    APPLICATION = "APPLICATION"
    FILE = "FILE"
    FOLDER = "FOLDER"
    WEBSITE = "WEBSITE"
    TOPIC = "TOPIC"
    PERSON = "PERSON"
    UNKNOWN = "UNKNOWN"

class EntityPriority(int, Enum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4

class TrackedEntity(BaseModel):
    """Represents a resolved entity tracked within the current session."""
    type: EntityType
    value: str
    priority: EntityPriority = EntityPriority.MEDIUM
    confidence: float = 1.0
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class AutomationContext(BaseModel):
    """Context isolated to local OS and Browser automation."""
    last_application: Optional[TrackedEntity] = None
    last_folder: Optional[TrackedEntity] = None
    last_file: Optional[TrackedEntity] = None
    last_website: Optional[TrackedEntity] = None
    recent_entities: List[TrackedEntity] = Field(default_factory=list)

class KnowledgeContext(BaseModel):
    """Context isolated to knowledge queries and LLM interactions."""
    current_topic: Optional[TrackedEntity] = None
    recent_concepts: List[TrackedEntity] = Field(default_factory=list)

class ConversationContext(BaseModel):
    """Context handling conversational state, confirmations, and history."""
    pending_confirmation: Optional[str] = None
    last_intent: Optional[str] = None
    recent_user_messages: List[str] = Field(default_factory=list)
    recent_assistant_messages: List[str] = Field(default_factory=list)

class SessionContext(BaseModel):
    """The master root for all short-term conversational context scopes."""
    session_id: str
    automation: AutomationContext = Field(default_factory=AutomationContext)
    knowledge: KnowledgeContext = Field(default_factory=KnowledgeContext)
    conversation: ConversationContext = Field(default_factory=ConversationContext)
    
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    last_activity: float = Field(default_factory=lambda: datetime.now().timestamp())
    
    def touch(self):
        """Updates the last_activity timestamp."""
        self.last_activity = datetime.now().timestamp()
