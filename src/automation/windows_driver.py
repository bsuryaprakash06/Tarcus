import uiautomation as auto
from typing import Optional, Any, List
from src.automation.driver import AutomationDriver
from src.models.ui_element import UIElement, UIElementHandle
from src.automation.tree_cache import TreeCache
from src.automation.locator import CompositeLocator
from src.utils.logger import get_logger

logger = get_logger("automation.windows_driver")

class WindowsDriver(AutomationDriver):
    def __init__(self):
        self.tree_cache = TreeCache()
        self.locator = CompositeLocator()
        
    @property
    def driver_name(self) -> str:
        return "windows"

    def find_window(self, name: str, class_name: str = None) -> Optional[UIElementHandle]:
        kwargs = {}
        if name:
            kwargs["Name"] = name
        if class_name:
            kwargs["ClassName"] = class_name
            
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
        
    def find_element(self, window: UIElementHandle, locator_strategy: Any, query: str) -> Optional[UIElementHandle]:
        nodes = self.tree_cache.get_tree(window.ui_element.id)
        if nodes is None:
            nodes = self.build_tree_cache(window)
            
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
        
    def click(self, element: UIElementHandle, double: bool = False, right: bool = False) -> bool:
        control = element.backend_reference
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
            
    def type_text(self, element: UIElementHandle, text: str, clear_first: bool = False) -> bool:
        control = element.backend_reference
        try:
            if clear_first:
                control.SendKeys('{Ctrl}a{Delete}')
            control.SendKeys(text)
            return True
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return False
            
    def focus(self, element: UIElementHandle) -> bool:
        control = element.backend_reference
        try:
            control.SetFocus()
            return True
        except Exception as e:
            logger.error(f"Focus failed: {e}")
            return False
            
    def scroll(self, element: UIElementHandle, direction: str, amount: int) -> bool:
        control = element.backend_reference
        try:
            if direction.lower() == "down":
                control.WheelDown(amount)
            else:
                control.WheelUp(amount)
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
            
    def read_text(self, element: UIElementHandle) -> str:
        control = element.backend_reference
        try:
            return control.Name or ""
        except Exception as e:
            logger.error(f"Read text failed: {e}")
            return ""
            
    def capture(self, element: Optional[UIElementHandle] = None) -> str:
        # Handled by separate screenshot provider
        return ""
