from pydantic import BaseModel

class BrowserStarted(BaseModel):
    browser_id: str
    
class BrowserClosed(BaseModel):
    browser_id: str
    
class BrowserAttached(BaseModel):
    browser_id: str
    
class BrowserDetached(BaseModel):
    browser_id: str
    
class SessionCreated(BaseModel):
    session_id: str
    browser_id: str

class SessionDestroyed(BaseModel):
    session_id: str
    
class TabCreated(BaseModel):
    session_id: str
    tab_id: str
    url: str

class TabClosed(BaseModel):
    session_id: str
    tab_id: str
    
class NavigationStarted(BaseModel):
    session_id: str
    tab_id: str
    url: str

class NavigationCompleted(BaseModel):
    session_id: str
    tab_id: str
    url: str
    success: bool
