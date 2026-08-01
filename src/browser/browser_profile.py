from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class BrowserProfile(BaseModel):
    id: str
    name: str
    user_data_dir: Optional[str] = None
    cookies: List[Dict[str, Any]] = Field(default_factory=list)
    permissions: Dict[str, str] = Field(default_factory=dict)
    downloads_path: Optional[str] = None
    persistent: bool = False
