from src.models.plan import ExecutionPlan
from src.tools.registry import ToolRegistry
from src.tools.base_tool import SafetyLevel
from src.utils.logger import get_logger
from src.utils.exceptions import VoiceAssistantError

logger = get_logger("safety.validator")

class SafetyError(VoiceAssistantError):
    """Exception raised when a tool execution is blocked due to safety violations."""
    pass

class SafetyValidator:
    """Validator layer verifying the safety levels of planned tool actions."""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        self.registry = tool_registry or ToolRegistry()

    def validate_plan(self, plan: ExecutionPlan) -> bool:
        """
        Inspects each item in the plan.
        - If any tool is BLOCKED or RESTRICTED, raises SafetyError.
        - If any tool requires confirmation, returns True (confirmation required).
        - Otherwise returns False (safe to run automatically).
        """
        needs_confirm = False
        
        for item in plan.plan:
            tool = self.registry.get_tool(item.tool)
            if not tool:
                # Untracked tool is safe to proceed (will fail execution)
                continue
                
            logger.info(f"Checking safety for tool '{tool.name}': level is {tool.safety_level.name}")
            
            if tool.safety_level == SafetyLevel.BLOCKED:
                logger.error(f"Execution blocked: tool '{tool.name}' is BLOCKED.")
                raise SafetyError(f"Action blocked: Tool '{tool.name}' is blocked on this system.")
                
            elif tool.safety_level == SafetyLevel.RESTRICTED:
                logger.error(f"Execution blocked: tool '{tool.name}' is RESTRICTED.")
                raise SafetyError(f"Action blocked: Tool '{tool.name}' is restricted.")
                
            elif tool.safety_level == SafetyLevel.CONFIRM:
                needs_confirm = True
                
        return needs_confirm
