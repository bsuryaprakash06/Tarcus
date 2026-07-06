from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class AutomationEntity(BaseModel):
    """Rich structured representation of an automation entity (e.g. an App or File)"""
    id: str
    type: str # "Application", "File", "Folder", "Website"
    name: str
    tool: str # e.g., "open_application"
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    last_accessed: float = Field(default_factory=lambda: datetime.now().timestamp())
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

from src.models.ui_element import UIElement

class AutomationSession(BaseModel):
    active_window: Optional[str] = None
    focused_element: Optional[UIElement] = None
    last_locator: Optional[str] = None
    last_action: Optional[str] = None
    current_backend: str = "windows"
    last_ui_snapshot: Optional[str] = None

class AutomationContext(BaseModel):
    """Memory bucket dedicated entirely to Automation elements"""
    session: AutomationSession = Field(default_factory=AutomationSession)
    recent_elements: List[UIElement] = Field(default_factory=list)
    applications: List[AutomationEntity] = Field(default_factory=list)
    files: List[AutomationEntity] = Field(default_factory=list)
    folders: List[AutomationEntity] = Field(default_factory=list)
    websites: List[AutomationEntity] = Field(default_factory=list)
    last_updated: float = Field(default_factory=lambda: datetime.now().timestamp())
    
    def add_entity(self, entity: AutomationEntity, category: str):
        target_list = getattr(self, category, None)
        if target_list is not None:
            # Prevent duplicates by name. Update if exists.
            for existing in target_list:
                if existing.name.lower() == entity.name.lower():
                    existing.last_accessed = datetime.now().timestamp()
                    existing.metadata.update(entity.metadata)
                    self.last_updated = datetime.now().timestamp()
                    return
                    
            # Entity Stack Behavior (Most Recent First)
            target_list.insert(0, entity) 
            if len(target_list) > 10:
                target_list.pop()
                
        self.last_updated = datetime.now().timestamp()
        
    def add_recent_element(self, element: UIElement):
        self.recent_elements.insert(0, element)
        if len(self.recent_elements) > 20:
            self.recent_elements.pop()
        self.session.focused_element = element
        self.last_updated = datetime.now().timestamp()

class KnowledgeContext(BaseModel):
    current_topic: Optional[str] = None
    previous_topic: Optional[str] = None
    last_updated: float = Field(default_factory=lambda: datetime.now().timestamp())

class ConversationContext(BaseModel):
    last_greeting: Optional[str] = None
    conversation_state: str = "IDLE"
    last_updated: float = Field(default_factory=lambda: datetime.now().timestamp())

class WorkflowContext(BaseModel):
    active_workflow: Optional[str] = None
    current_step: Optional[str] = None
    pending_confirmation: bool = False
    last_updated: float = Field(default_factory=lambda: datetime.now().timestamp())

class SystemContext(BaseModel):
    os: str = "Windows"
    current_directory: Optional[str] = None
    current_user: Optional[str] = None
    last_updated: float = Field(default_factory=lambda: datetime.now().timestamp())
