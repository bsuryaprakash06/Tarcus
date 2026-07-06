import threading
from typing import Dict, List, Optional
from src.models.target import Target, TargetLifecycle
from src.utils.logger import get_logger

logger = get_logger("automation.target_registry")

class TargetRegistry:
    """
    Central, thread-safe registry of all targets across all automation backends.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TargetRegistry, cls).__new__(cls)
            cls._instance._lock = threading.Lock()
            cls._instance._targets: Dict[str, Target] = {}
            cls._instance._next_id = 1
        return cls._instance

    def _generate_id(self) -> str:
        tid = f"target_{self._next_id:04d}"
        self._next_id += 1
        return tid

    def register_target(self, target_def: Target) -> Target:
        """
        Registers a new target if its native_handle doesn't already exist.
        Otherwise, updates and returns the existing target.
        """
        with self._lock:
            # Check if exists by native handle
            if target_def.native_handle:
                for existing in self._targets.values():
                    if existing.native_handle == target_def.native_handle and existing.backend == target_def.backend:
                        existing.name = target_def.name
                        existing.lifecycle_state = target_def.lifecycle_state
                        existing.capabilities = target_def.capabilities
                        return existing

            # Register new
            target_def.id = self._generate_id()
            if target_def.lifecycle_state == TargetLifecycle.DISCOVERED:
                target_def.lifecycle_state = TargetLifecycle.AVAILABLE
                
            self._targets[target_def.id] = target_def
            logger.info(f"Registered new Target: {target_def.id} ({target_def.name})")
            return target_def

    def update_lifecycle(self, target_id: str, new_state: TargetLifecycle):
        with self._lock:
            if target_id in self._targets:
                self._targets[target_id].lifecycle_state = new_state
                logger.debug(f"Target {target_id} lifecycle -> {new_state.value}")

    def get_target(self, target_id: str) -> Optional[Target]:
        with self._lock:
            return self._targets.get(target_id)

    def list_targets(self, active_only: bool = True) -> List[Target]:
        with self._lock:
            if active_only:
                return [t for t in self._targets.values() if t.lifecycle_state not in (TargetLifecycle.CLOSED, TargetLifecycle.DISCOVERED)]
            return list(self._targets.values())
