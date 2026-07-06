import uiautomation as auto
from typing import Optional, Any, List
from src.automation.driver import AutomationBackend
from src.models.ui_element import UIElement, UIElementHandle
from src.models.target import Target, TargetType, TargetLifecycle, TargetCapability
from src.models.interaction import InteractionContext
from src.automation.tree_cache import TreeCache
from src.automation.locator import CompositeLocator
from src.utils.logger import get_logger

logger = get_logger("automation.windows_driver")

class WindowsDriver(AutomationBackend):
    def __init__(self):
        self.tree_cache = TreeCache()
        self.locator = CompositeLocator()
        
    @property
    def backend_name(self) -> str:
        return "windows_uia"

    def discover_targets(self) -> List[Target]:
        import uiautomation as auto
        targets = []
        for win in auto.GetRootControl().GetChildren():
            if win.ControlTypeName == 'WindowControl' and win.Name:
                t = Target(
                    id="", # Assigned by registry
                    type=TargetType.WINDOW,
                    backend=self.backend_name,
                    name=win.Name,
                    native_handle=str(win.NativeWindowHandle),
                    lifecycle_state=TargetLifecycle.DISCOVERED,
                    capabilities=[TargetCapability.TYPING, TargetCapability.CLICKING, TargetCapability.READING, TargetCapability.SCROLLING]
                )
                targets.append(t)
        return targets

    def activate_target(self, target: Target) -> bool:
        import uiautomation as auto
        if not target.native_handle: return False
        try:
            win = auto.WindowControl(searchDepth=1, NativeWindowHandle=int(target.native_handle))
            if win.Exists(0, 0):
                win.SetFocus()
                return True
        except:
            pass
        return False
            
        auto.SetGlobalSearchTimeout(1.0) # We handle our own retry loops
        try:
            win = auto.WindowControl(**kwargs)
            if win.Exists(0, 0):
                rect = win.BoundingRectangle
                el = UIElement(
                    id=str(win.NativeWindowHandle),
                    name=win.Name,
                    automation_id=win.AutomationId,
                    class_name=win.ClassName,
                    control_type=win.ControlTypeName,
                    bounding_rectangle=[rect.left, rect.top, rect.right, rect.bottom]
                )
                return UIElementHandle(backend_reference=win, cached_locator=name, ui_element=el)
        except Exception as e:
            logger.error(f"Failed to find window {name}: {e}")
        return None
        
    def build_tree_cache(self, window: UIElementHandle) -> List[Any]:
        win_control = window.backend_reference
        nodes = []
        for control, depth in auto.WalkControl(win_control, includeTop=True):
            nodes.append(control)
        
        self.tree_cache.set_tree(window.ui_element.id, nodes)
        return nodes
        
    def find_element(self, context: InteractionContext, query: str) -> Optional[UIElementHandle]:
        if not context.current_target or not context.current_target.native_handle: return None
        
        # We need the root UIElementHandle for the window
        import uiautomation as auto
        win_control = auto.WindowControl(searchDepth=1, NativeWindowHandle=int(context.current_target.native_handle))
        if not win_control.Exists(0,0): return None
        
        # Fast query cache logic
        nodes = []
        for control, depth in auto.WalkControl(win_control, includeTop=True):
            nodes.append(control)
            
        best_node, score = self.locator.find_best_match(nodes, query)
        if best_node:
            try:
                rect = best_node.BoundingRectangle
                bounds = [rect.left, rect.top, rect.right, rect.bottom]
            except Exception:
                bounds = None
                
            el = UIElement(
                id=str(id(best_node)),
                name=getattr(best_node, "Name", ""),
                automation_id=getattr(best_node, "AutomationId", ""),
                class_name=getattr(best_node, "ClassName", ""),
                control_type=getattr(best_node, "ControlTypeName", ""),
                bounding_rectangle=bounds
            )
            return UIElementHandle(backend_reference=best_node, cached_locator=query, ui_element=el)
        return None
        
    def click(self, context: InteractionContext, double: bool = False, right: bool = False) -> bool:
        if not context.focused_element: return False
        control = context.focused_element.backend_reference
        try:
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
            
    def type_text(self, context: InteractionContext, text: str, clear_first: bool = False) -> bool:
        if not context.focused_element: return False
        control = context.focused_element.backend_reference
        try:
            if clear_first:
                control.SendKeys('{Ctrl}a{Delete}')
            control.SendKeys(text)
            return True
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return False
            
    def focus_element(self, context: InteractionContext) -> bool:
        if not context.focused_element: return False
        control = context.focused_element.backend_reference
        try:
            control.SetFocus()
            return True
        except Exception as e:
            logger.error(f"Focus failed: {e}")
            return False
            
    def scroll(self, context: InteractionContext, direction: str, amount: int) -> bool:
        if not context.focused_element: return False
        control = context.focused_element.backend_reference
        try:
            if direction.lower() == "down":
                control.WheelDown(amount)
            else:
                control.WheelUp(amount)
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
            
    def read_text(self, context: InteractionContext) -> str:
        if not context.focused_element: return ""
        control = context.focused_element.backend_reference
        try:
            return control.Name or ""
        except Exception as e:
            logger.error(f"Read text failed: {e}")
            return ""
            
    def capture(self, context: InteractionContext) -> str:
        return ""
