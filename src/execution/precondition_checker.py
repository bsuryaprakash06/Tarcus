import time
from typing import Dict, Any, Tuple
from src.models.workflow_execution import Precondition
from src.automation.focus_manager import FocusManager
from src.automation.target_registry import TargetRegistry
from src.models.target import TargetCapability
from src.utils.logger import get_logger

from src.automation.windows_driver import WindowsDriver

logger = get_logger("execution.precondition_checker")

class PreconditionChecker:
    """
    Checks preconditions before a step executes.
    Crucially, attempts recovery (e.g. focusing a window) before failing.
    """
    
    def __init__(self):
        self.target_registry = TargetRegistry()
        self.focus_manager = FocusManager(WindowsDriver())
        
    def check_and_recover(self, precondition: Precondition, context: Any) -> Tuple[bool, str]:
        """Returns (success, error_message). Attempts recovery if needed."""
        
        target_id = precondition.target_id
        if not target_id and getattr(context, "interaction", None) and context.interaction.current_target:
            target_id = context.interaction.current_target.id
            
        if not target_id:
            # Some preconditions don't need a target, but if it does and it's missing:
            if precondition.type in ["TARGET_CAPABLE", "WINDOW_FOCUSED", "WINDOW_EXISTS"]:
                return False, "No active target specified in context or precondition."
                
        target = self.target_registry.get_target(target_id) if target_id else None
                
        if precondition.type == "WINDOW_EXISTS":
            if not target:
                return False, f"Target {target_id} does not exist in registry."
            return True, ""
            
        elif precondition.type == "WINDOW_FOCUSED":
            # Check
            is_ready, msg = self.focus_manager.ensure_focused(target)
            if not is_ready:
                # Recover
                logger.info(f"Precondition recovery: Attempting to focus target {target_id}")
                success = self.focus_manager.focus_target(target_id)
                if not success:
                    return False, f"Recovery failed: Could not focus target {target_id}"
                
                # Check Again
                time.sleep(0.5) # Give UI time to respond
                is_ready, msg = self.focus_manager.ensure_focused(target)
                if not is_ready:
                    return False, f"Recovery failed: Target {target_id} still not focused. {msg}"
            return True, ""
            
        elif precondition.type == "TARGET_CAPABLE":
            req_capability_str = precondition.parameters.get("capability")
            try:
                req_capability = TargetCapability[req_capability_str]
            except KeyError:
                return False, f"Unknown capability {req_capability_str}"
                
            if not target or req_capability not in target.capabilities:
                return False, f"Target {target_id} does not support {req_capability_str}"
            return True, ""
            
        # Add more preconditions as needed
        
        return True, ""
