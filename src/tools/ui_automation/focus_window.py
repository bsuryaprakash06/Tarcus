import time
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.automation.windows_driver import WindowsDriver
from src.automation.action_executor import ActionExecutor
from src.utils.settings import DRY_RUN

class FocusWindowTool(BaseTool):
    @property
    def name(self) -> str:
        return "focus_window"
        
    @property
    def description(self) -> str:
        return "Brings a specific application window to the foreground."
        
    @property
    def arguments_schema(self) -> dict:
        return {
            "window": {
                "type": "string",
                "description": "Name of the window to focus (e.g. 'Notepad')"
            }
        }
        
    @property
    def examples(self) -> list[str]:
        return ["Focus Notepad", "Switch to Chrome", "Bring Calculator to the front"]
        
    @property
    def category(self) -> str:
        return "UI Automation"
        
    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        window_name = arguments.get("window")
        if not window_name:
            return ToolResult(tool_name=self.name, success=False, user_message="Missing window name.", developer_message="Missing arg: window", duration=0.0)
            
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"[DRY RUN] Would focus window: {window_name}", developer_message="", duration=0.0)
            
        driver = WindowsDriver()
        executor = ActionExecutor(driver)
        
        start_time = time.time()
        try:
            handle = driver.find_window(window_name)
            if not handle:
                return ToolResult(tool_name=self.name, success=False, user_message=f"Could not find window: {window_name}", developer_message="Driver returned None", duration=0.0)
            
            result = executor.focus(handle)
            
            if result.success and context and getattr(context, "automation", None):
                context.automation.session.active_window = handle.ui_element.name
                
            return ToolResult(
                tool_name=self.name,
                success=result.success,
                user_message=f"Focused {window_name}." if result.success else f"Failed to focus {window_name}.",
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
