from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import datetime

class BrowserType(str, Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    EDGE = "edge"
    UNKNOWN = "unknown"

class BrowserStatus(str, Enum):
    CLOSED = "closed"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"

class TabStatus(str, Enum):
    LOADING = "loading"
    READY = "ready"
    CLOSED = "closed"

class BrowserTab(BaseModel):
    id: str
    url: str
    title: str = ""
    status: TabStatus = TabStatus.LOADING
    created_at: float = Field(default_factory=lambda: datetime.datetime.now().timestamp())

class HistoryEntry(BaseModel):
    url: str
    title: str
    timestamp: float
    navigation_type: str = "navigate" # navigate, back, forward, refresh
    status: str = "success"

class BrowserSession(BaseModel):
    session_id: str
    tabs: Dict[str, BrowserTab] = Field(default_factory=dict)
    active_tab_id: Optional[str] = None
    history: List[HistoryEntry] = Field(default_factory=list)
    cookies: List[Dict[str, Any]] = Field(default_factory=list)
    downloads: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BrowserInstance(BaseModel):
    id: str
    browser_type: BrowserType
    status: BrowserStatus = BrowserStatus.CLOSED
    process_id: Optional[int] = None
    
    # Internal references that aren't serialized
    class Config:
        arbitrary_types_allowed = True
        
    playwright_browser: Any = None
    backend: Any = None
