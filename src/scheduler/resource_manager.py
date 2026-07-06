import threading
from typing import Dict, Set
from src.utils.logger import get_logger
from src.models.scheduler import ResourceLock, ResourceType

logger = get_logger("scheduler.resource_manager")

class ResourceManager:
    """
    Manages exclusive access to system resources (Applications, Browsers, Devices, etc.)
    Ensures that tasks with exclusive resource requirements do not run concurrently.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._lock = threading.Lock()
            # Dictionary mapping resource keys (e.g., "APPLICATION:Notepad") to the owning Node ID
            cls._instance._active_locks: Dict[str, str] = {}
        return cls._instance
        
    def _get_key(self, lock: ResourceLock) -> str:
        return f"{lock.resource_type.value}:{lock.identifier.lower()}"
        
    def acquire_locks(self, node_id: str, required_locks: list[ResourceLock]) -> bool:
        """
        Attempts to acquire all specified locks atomically.
        Returns True if successful, False if any lock is currently held by another node.
        """
        if not required_locks:
            return True
            
        with self._lock:
            # First, check if all required locks are available
            for lock in required_locks:
                if lock.exclusive:
                    key = self._get_key(lock)
                    if key in self._active_locks and self._active_locks[key] != node_id:
                        logger.debug(f"Node {node_id} failed to acquire lock {key} (held by {self._active_locks[key]})")
                        return False
                        
            # All available, acquire them
            for lock in required_locks:
                if lock.exclusive:
                    key = self._get_key(lock)
                    self._active_locks[key] = node_id
                    logger.debug(f"Node {node_id} acquired resource lock: {key}")
                    
            return True
            
    def release_locks(self, node_id: str):
        """Releases all locks held by the specified node."""
        with self._lock:
            released = []
            for key, owner_id in list(self._active_locks.items()):
                if owner_id == node_id:
                    del self._active_locks[key]
                    released.append(key)
                    
            if released:
                logger.debug(f"Node {node_id} released resource locks: {', '.join(released)}")
