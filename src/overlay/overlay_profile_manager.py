from enum import Enum
from pydantic import BaseModel

class ProfileType(str, Enum):
    WINDOW = "WINDOW"
    BROWSER = "BROWSER"
    VISION = "VISION"
    PLUGIN = "PLUGIN"
    REMOTE = "REMOTE"

class OverlayProfile(BaseModel):
    profile_type: ProfileType
    border_style: str = "solid"
    show_badge: bool = True
    show_bounds: bool = True

class OverlayProfileManager:
    """
    Separates appearance logic from rendering. Allows targets to have entirely different
    visual styles based on their nature (e.g., standard UI window vs. a vision bounding box).
    """
    def __init__(self):
        self.profiles = {
            ProfileType.WINDOW: OverlayProfile(profile_type=ProfileType.WINDOW),
            ProfileType.BROWSER: OverlayProfile(profile_type=ProfileType.BROWSER, border_style="solid"),
            ProfileType.VISION: OverlayProfile(profile_type=ProfileType.VISION, border_style="dashed"),
            ProfileType.PLUGIN: OverlayProfile(profile_type=ProfileType.PLUGIN, border_style="dashed"),
            ProfileType.REMOTE: OverlayProfile(profile_type=ProfileType.REMOTE, border_style="solid")
        }

    def resolve_profile(self, target_properties: dict) -> OverlayProfile:
        """
        Determines the appropriate profile based on the interaction target's properties.
        """
        # In the future, check properties like "type": "vision", etc.
        # For now, default to WINDOW
        target_type = target_properties.get("backend", "windows").upper()
        
        if target_type == "VISION":
            return self.profiles[ProfileType.VISION]
        elif target_type == "BROWSER":
            return self.profiles[ProfileType.BROWSER]
            
        return self.profiles[ProfileType.WINDOW]
