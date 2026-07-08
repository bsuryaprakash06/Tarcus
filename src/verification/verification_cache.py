import time
from typing import Dict, Tuple

class VerificationCache:
    """
    Prevents redundant OS calls by caching verification results for a short duration.
    """
    def __init__(self, ttl_seconds: float = 0.5):
        self.ttl_seconds = ttl_seconds
        # Key: (target_id, rule_name), Value: (result, timestamp)
        self._cache: Dict[Tuple[str, str], Tuple[bool, float]] = {}

    def get(self, target_id: str, rule_name: str) -> bool:
        """Returns the cached result if within TTL, else None."""
        key = (target_id, rule_name)
        if key in self._cache:
            result, timestamp = self._cache[key]
            if (time.time() - timestamp) <= self.ttl_seconds:
                return result
            else:
                del self._cache[key]
        return None

    def set(self, target_id: str, rule_name: str, result: bool):
        key = (target_id, rule_name)
        self._cache[key] = (result, time.time())

    def clear(self, target_id: str = None):
        if target_id:
            keys_to_delete = [k for k in self._cache.keys() if k[0] == target_id]
            for k in keys_to_delete:
                del self._cache[k]
        else:
            self._cache.clear()
