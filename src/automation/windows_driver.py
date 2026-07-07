import uiautomation as auto
from typing import Optional, List, Dict, Any
from src.automation.driver import AutomationBackend
from src.models.target import InteractionTarget, TargetSession, Platform
from src.models.interaction_graph import InteractionGraph
from src.utils.logger import get_logger

logger = get_logger("automation.windows_driver")

class WindowsDriver(AutomationBackend):
    @property
    def backend_name(self) -> str:
        return "WINDOWS_UIA"

    def discover(self) -> InteractionGraph:
        """Discovers top-level windows and returns a basic InteractionGraph."""
        desktop = auto.GetRootControl()
        graph = InteractionGraph(root_id="desktop")
        
        desktop_target = InteractionTarget(
            id="desktop",
            platform=Platform.WINDOWS,
            backend=self.backend_name,
            native_handle=str(desktop.NativeWindowHandle) if hasattr(desktop, "NativeWindowHandle") else None,
            friendly_name="Desktop"
        )
        graph.add_node(desktop_target)
        
        for win in desktop.GetChildren():
            if win.ControlTypeName == 'WindowControl' and win.Name:
                tid = f"target_window_{win.NativeWindowHandle}"
                t = InteractionTarget(
                    id=tid,
                    platform=Platform.WINDOWS,
                    backend=self.backend_name,
                    native_handle=str(win.NativeWindowHandle),
                    pid=win.ProcessId if hasattr(win, 'ProcessId') else None,
                    friendly_name=win.Name
                )
                graph.add_node(t, parent_id="desktop")
        return graph
        
    def resolve(self, session: TargetSession, query: str) -> Optional[InteractionTarget]:
        """Resolves a child control within the target's handle."""
        if not session.target.native_handle:
            return None
            
        win = auto.ControlFromHandle(int(session.target.native_handle))
        if not win:
            return None
            
        # Very basic resolution logic for demonstration
        for child, depth in auto.WalkControl(win, includeTop=False, maxDepth=3):
            if query.lower() in child.Name.lower() or query.lower() in child.ControlTypeName.lower() or query.lower() in child.AutomationId.lower():
                tid = f"target_control_{id(child)}"
                return InteractionTarget(
                    id=tid,
                    platform=Platform.WINDOWS,
                    backend=self.backend_name,
                    native_handle=str(child.NativeWindowHandle) if hasattr(child, "NativeWindowHandle") and child.NativeWindowHandle else None,
                    pid=child.ProcessId if hasattr(child, "ProcessId") else session.target.pid,
                    friendly_name=child.Name or child.ControlTypeName
                )
        return None
        
    def focus(self, session: TargetSession) -> bool:
        if not session.target.native_handle:
            return False
        try:
            control = auto.ControlFromHandle(int(session.target.native_handle))
            if control:
                control.SetFocus()
                return True
        except Exception as e:
            logger.error(f"Focus failed: {e}")
        return False

    def click(self, session: TargetSession, double: bool = False, right: bool = False) -> bool:
        if not session.target.native_handle:
            return False
        try:
            control = auto.ControlFromHandle(int(session.target.native_handle))
            if control:
                if right:
                    control.RightClick()
                elif double:
                    control.DoubleClick()
                else:
                    control.Click()
                return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
        return False
        
    def type(self, session: TargetSession, text: str, clear_first: bool = False) -> bool:
        from src.automation.strategies.text_insertion import UIAutomationValuePatternStrategy, KeyboardSimulationStrategy
        
        # Try UIAutomation first
        if UIAutomationValuePatternStrategy().execute(session, text, clear_first):
            return True
            
        # Fallback to Keyboard
        return KeyboardSimulationStrategy().execute(session, text, clear_first)
        
    def read(self, session: TargetSession) -> str:
        if not session.target.native_handle:
            return ""
        try:
            control = auto.ControlFromHandle(int(session.target.native_handle))
            if control:
                return control.Name or ""
        except Exception:
            pass
        return ""
        
    def scroll(self, session: TargetSession, direction: str, amount: int) -> bool:
        if not session.target.native_handle:
            return False
        try:
            control = auto.ControlFromHandle(int(session.target.native_handle))
            if control:
                if direction.lower() == "down":
                    control.WheelDown(amount)
                else:
                    control.WheelUp(amount)
                return True
        except Exception:
            pass
        return False
        
    def capture(self, session: TargetSession) -> str:
        return ""
        
    def verify(self, session: TargetSession, condition: Dict[str, Any]) -> bool:
        # Example condition check: native handle still valid?
        if not session.target.native_handle:
            return False
        try:
            control = auto.ControlFromHandle(int(session.target.native_handle))
            return control.Exists(0, 0)
        except Exception:
            return False
