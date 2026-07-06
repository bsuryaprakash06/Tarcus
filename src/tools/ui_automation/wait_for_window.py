import time
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.automation.windows_driver import WindowsDriver
from src.automation.wait_manager import WaitManager
from src.utils.settings import DRY_RUN

class WaitForWindowTool(BaseTool):
    @property
    def name(self) -> str:
        return "wait_for_window"
        
    @property
    def description(self) -> str:
        return "Pauses workflow execution until a specific window appears."
        
    @property
    def arguments_schema(self) -> dict:
        return {
            "window": "Name of the window to wait for."
        }
        
    @property
    def examples(self) -> list[str]:
        return ["Wait for Notepad", "Wait until Calculator opens"]
        
    @property
    def category(self) -> str:
        return "UI Automation"
        
    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        window_name = arguments.get("window")
        if not window_name:
            return ToolResult(tool_name=self.name, success=False, user_message="Missing window name.", developer_message="Missing arg: window", duration=0.0)
            
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"[DRY RUN] Would wait for window: {window_name}", developer_message="", duration=0.0)
            
        driver = WindowsDriver()
        
        start_time = time.time()
        try:
            success = WaitManager.wait_for_window(driver, window_name, timeout=10.0)
            
            return ToolResult(
                tool_name=self.name,
                success=success,
                user_message=f"Window {window_name} appeared." if success else f"Timed out waiting for {window_name}.",
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
