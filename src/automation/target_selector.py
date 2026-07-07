import threading
from typing import Optional
from src.models.target import InteractionTarget
from src.utils.logger import get_logger

logger = get_logger("automation.target_selector")

class TargetSelector:
    """
    Maintains the global 'Current Target' for the interaction context.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TargetSelector, cls).__new__(cls)
            cls._instance._lock = threading.Lock()
            cls._instance._current_target: Optional[InteractionTarget] = None
        return cls._instance
        
    def set_current_target(self, target: InteractionTarget):
        with self._lock:
            self._current_target = target
            logger.info(f"Current Target set to: {target.id} ({target.friendly_name})")
            
    def get_current_target(self) -> Optional[InteractionTarget]:
        with self._lock:
            return self._current_target
            
    def clear(self):
        with self._lock:
            self._current_target = None
