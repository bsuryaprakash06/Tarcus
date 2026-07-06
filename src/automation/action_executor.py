from src.automation.driver import AutomationDriver
from src.models.ui_element import UIElementHandle, AutomationResult
from src.utils.logger import get_logger
import time

logger = get_logger("automation.executor")

class ActionExecutor:
    """Strictly executes actions on resolved handles. No searching permitted."""
    
    def __init__(self, driver: AutomationDriver):
        self.driver = driver
        
    def click(self, handle: UIElementHandle, double: bool = False, right: bool = False) -> AutomationResult:
        start_time = time.time()
        success = self.driver.click(handle, double, right)
        duration = time.time() - start_time
        return AutomationResult(success=success, duration=duration, element=handle.ui_element, backend=self.driver.driver_name)
        
    def type_text(self, handle: UIElementHandle, text: str, clear_first: bool = False) -> AutomationResult:
        start_time = time.time()
        success = self.driver.type_text(handle, text, clear_first)
        duration = time.time() - start_time
        return AutomationResult(success=success, duration=duration, element=handle.ui_element, backend=self.driver.driver_name)
        
    def focus(self, handle: UIElementHandle) -> AutomationResult:
        start_time = time.time()
        success = self.driver.focus(handle)
        duration = time.time() - start_time
        return AutomationResult(success=success, duration=duration, element=handle.ui_element, backend=self.driver.driver_name)
