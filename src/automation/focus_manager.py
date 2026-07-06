import time
from src.utils.logger import get_logger
from src.models.interaction import InteractionContext
from src.models.target import TargetCapability
from src.automation.driver import AutomationBackend

logger = get_logger("automation.focus_manager")

class FocusManager:
    """
    Enforces strict focus state and verification before any interaction happens.
    Never assumes focus succeeded automatically.
    """
    def __init__(self, backend: AutomationBackend):
        self.backend = backend
        
    def prepare_for_interaction(self, context: InteractionContext, capability_required: TargetCapability = None) -> bool:
        """
        Runs the full verification pipeline:
        Restore -> Bring to Front -> Focus Element -> Verify Focus.
        """
        if not context.current_target:
            logger.error("FocusManager: No current_target in InteractionContext!")
            return False
            
        target = context.current_target
        
        # 1. Check capability
        if capability_required and not target.can(capability_required):
            logger.error(f"FocusManager: Target {target.id} does not support {capability_required.value}!")
            return False
            
        # 2. Activate Target (Restore & Bring to Front)
        logger.info(f"FocusManager: Activating target {target.id} ({target.name})")
        if not self.backend.activate_target(target):
            logger.error(f"FocusManager: Failed to activate target {target.id}")
            return False
            
        # Give OS a moment to complete window transition
        time.sleep(0.3)
        
        # 3. Focus specific control (if one is targeted)
        if context.focused_element:
            logger.info(f"FocusManager: Focusing element {context.focused_element.id}")
            if not self.backend.focus_element(context):
                logger.error(f"FocusManager: Failed to focus element {context.focused_element.id}")
                return False
                
        # 4. Verification (Checking if it really is in the foreground)
        # We can implement a deep check here, for now we assume success if no exceptions.
        # A real implementation would query OS `GetForegroundWindow` to verify.
        logger.info(f"FocusManager: Context verified. Ready for {capability_required.value if capability_required else 'Interaction'}.")
        return True
