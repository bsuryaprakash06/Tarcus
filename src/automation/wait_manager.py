import time
from typing import Callable, Any
from src.utils.logger import get_logger

logger = get_logger("automation.wait_manager")

class WaitManager:
    """Event-driven condition waiters replacing fragile time.sleep()."""
    
    @staticmethod
    def wait_until(condition: Callable[[], bool], timeout: float = 10.0, poll_freq: float = 0.5) -> bool:
        """Polls the condition until True or timeout occurs."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if condition():
                    return True
            except Exception:
                pass
            time.sleep(poll_freq)
        return False
        
    @staticmethod
    def wait_until_visible(driver: Any, window: Any, locator: Any, query: str, timeout: float = 10.0) -> bool:
        def condition():
            el = driver.find_element(window, locator, query)
            return el is not None
        return WaitManager.wait_until(condition, timeout=timeout)
        
    @staticmethod
    def wait_for_window(driver: Any, name: str, timeout: float = 10.0) -> bool:
        from src.automation.window_manager import WindowManager
        def condition():
            windows = WindowManager.list_open_windows()
            return any(name.lower() in w.lower() for w in windows)
        return WaitManager.wait_until(condition, timeout=timeout)
