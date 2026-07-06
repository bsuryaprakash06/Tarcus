import time
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.automation.windows_driver import WindowsDriver
from src.automation.action_executor import ActionExecutor
from src.utils.settings import DRY_RUN

class ScrollWindowTool(BaseTool):
    @property
    def name(self) -> str:
        return "scroll_window"
        
    @property
    def description(self) -> str:
        return "Scrolls the currently focused element up or down."
        
    @property
    def arguments_schema(self) -> dict:
        return {
            "direction": {
                "type": "string",
                "optional": True,
                "description": "Direction to scroll ('up' or 'down')."
            },
            "amount": {
                "type": "integer",
                "optional": True,
                "description": "Number of scroll ticks (default 1)."
            }
        }
        
    @property
    def examples(self) -> list[str]:
        return ["Scroll down", "Scroll up", "Scroll down a lot"]
        
    @property
    def category(self) -> str:
        return "UI Automation"
        
    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        direction = arguments.get("direction", "down")
        amount = int(arguments.get("amount", 1))
        
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"[DRY RUN] Would scroll {direction} by {amount}", developer_message="", duration=0.0)
            
        start_time = time.time()
        try:
            interaction = context.interaction if context else None
            if not interaction or not interaction.current_target:
                return ToolResult(tool_name=self.name, success=False, user_message="No active target to scroll.", developer_message="InteractionContext missing or empty", duration=0.0)
                
            from src.models.target import TargetCapability
            if not interaction.current_target.can(TargetCapability.SCROLLING):
                return ToolResult(tool_name=self.name, success=False, user_message="The current target does not support scrolling.", developer_message=f"Target lacks SCROLLING capability", duration=0.0)
                
            from src.automation.windows_driver import WindowsDriver
            from src.automation.focus_manager import FocusManager
            
            backend = WindowsDriver() 
            focus_manager = FocusManager(backend)
            
            if not focus_manager.prepare_for_interaction(interaction, TargetCapability.SCROLLING):
                return ToolResult(tool_name=self.name, success=False, user_message="Failed to focus the target element.", developer_message="FocusManager rejected interaction", duration=0.0)
                
            success = backend.scroll(interaction, direction, amount)
            
            return ToolResult(
                tool_name=self.name,
                success=success,
                user_message=f"Scrolled {direction}.",
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
