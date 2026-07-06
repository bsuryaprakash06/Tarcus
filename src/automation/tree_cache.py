from typing import Dict, Any, Optional
from src.utils.logger import get_logger

logger = get_logger("automation.tree_cache")

class TreeCache:
    """In-memory UI tree cache to drastically minimize expensive OS-level API calls."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TreeCache, cls).__new__(cls)
            cls._instance._cache = {} # Keyed by window ID
        return cls._instance
        
    def get_tree(self, window_id: str) -> Optional[Any]:
        return self._cache.get(window_id)
        
    def set_tree(self, window_id: str, tree: Any):
        self._cache[window_id] = tree
        logger.debug(f"Cached UI Tree for window {window_id}")
        
    def invalidate(self, window_id: str):
        if window_id in self._cache:
            del self._cache[window_id]
            logger.debug(f"Invalidated UI Tree cache for window {window_id}")
            
    def invalidate_all(self):
        self._cache.clear()
        logger.debug("Invalidated all UI Tree caches.")
