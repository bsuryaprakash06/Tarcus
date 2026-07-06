import time
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.automation.windows_driver import WindowsDriver
from src.utils.settings import DRY_RUN

class ReadTextTool(BaseTool):
    @property
    def name(self) -> str:
        return "read_text"
        
    @property
    def description(self) -> str:
        return "Reads visible text from a specific UI element."
        
    @property
    def arguments_schema(self) -> dict:
        return {
            "element_name": {
                "type": "string",
                "description": "The name of the element to read from."
            }
        }
        
    @property
    def examples(self) -> list[str]:
        return ["Read the label", "What does the text say?"]
        
    @property
    def category(self) -> str:
        return "UI Automation"
        
    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        element_name = arguments.get("element_name")
        if not element_name:
            return ToolResult(tool_name=self.name, success=False, user_message="Missing element name.", developer_message="Missing arg: element_name", duration=0.0)
            
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"[DRY RUN] Would read text from: '{element_name}'", developer_message="", duration=0.0)
            
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
            
            el_handle = driver.find_element(win_handle, None, element_name)
            if not el_handle:
                return ToolResult(tool_name=self.name, success=False, user_message=f"Could not find element: {element_name}", developer_message="", duration=0.0)
                
            text = driver.read_text(el_handle)
            
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=text,
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
