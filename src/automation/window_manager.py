import psutil
import uiautomation as auto
from typing import List, Optional
from src.utils.logger import get_logger

logger = get_logger("automation.window_manager")

class WindowManager:
    """Manages process windows: focus, maximize, minimize, close."""
    
    @staticmethod
    def list_open_windows() -> List[str]:
        windows = []
        for win in auto.GetRootControl().GetChildren():
            if win.ControlTypeName == 'WindowControl' and win.Name:
                windows.append(win.Name)
        return windows
        
    @staticmethod
    def get_foreground_window() -> Optional[str]:
        # Using uiautomation to get focused control then walk up to WindowControl
        focused = auto.GetFocusedControl()
        if not focused:
            return None
        # Walk up the tree to find the window
        current = focused
        while current and current.ControlTypeName != 'WindowControl':
            current = current.GetParentControl()
        return current.Name if current else None
        
    @staticmethod
    def activate_window(name_substring: str) -> bool:
        for win in auto.GetRootControl().GetChildren():
            if win.ControlTypeName == 'WindowControl' and win.Name and name_substring.lower() in win.Name.lower():
                try:
                    win.SetFocus()
                    return True
                except Exception as e:
                    logger.error(f"Failed to activate window: {e}")
        return False
        
    @staticmethod
    def close_window(name_substring: str) -> bool:
        for win in auto.GetRootControl().GetChildren():
            if win.ControlTypeName == 'WindowControl' and win.Name and name_substring.lower() in win.Name.lower():
                try:
                    win.GetWindowPattern().Close()
                    return True
                except Exception as e:
                    logger.error(f"Failed to close window: {e}")
        return False
