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
            "direction": "Direction to scroll ('up' or 'down').",
            "amount": "Number of scroll ticks (default 1)."
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
            
        driver = WindowsDriver()
        
        start_time = time.time()
        try:
            active_window_name = context.automation.session.active_window if context and getattr(context, "automation", None) else None
            if not active_window_name:
                from src.automation.window_manager import WindowManager
                active_window_name = WindowManager.get_foreground_window()
                
            if not active_window_name:
                return ToolResult(tool_name=self.name, success=False, user_message="No active window.", developer_message="active_window is None", duration=0.0)
                
            win_handle = driver.find_window(active_window_name)
            if not win_handle:
                return ToolResult(tool_name=self.name, success=False, user_message="Active window lost.", developer_message="", duration=0.0)
            
            success = driver.scroll(win_handle, direction, amount)
            
            if success and context and getattr(context, "automation", None):
                context.automation.session.last_action = "SCROLL"
                
            return ToolResult(
                tool_name=self.name,
                success=success,
                user_message=f"Scrolled {direction}.",
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
