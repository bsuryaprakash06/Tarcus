import time
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.automation.windows_driver import WindowsDriver
from src.automation.action_executor import ActionExecutor
from src.utils.settings import DRY_RUN

class TypeTextTool(BaseTool):
    @property
    def name(self) -> str:
        return "type_text"
        
    @property
    def description(self) -> str:
        return "Types text into the currently focused UI element (or the active window if no element specified)."
        
    @property
    def arguments_schema(self) -> dict:
        return {
            "text": "The text to type.",
            "element_name": "Optional. The name of the element to type into.",
            "clear_first": "Boolean indicating whether to clear the field first (default false)."
        }
        
    @property
    def examples(self) -> list[str]:
        return ["Type Hello into the editor", "Type 5", "Enter my name"]
        
    @property
    def category(self) -> str:
        return "UI Automation"
        
    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        text = arguments.get("text")
        if not text:
            return ToolResult(tool_name=self.name, success=False, user_message="Missing text to type.", developer_message="Missing arg: text", duration=0.0)
            
        element_name = arguments.get("element_name")
        clear_first = arguments.get("clear_first", False)
        
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"[DRY RUN] Would type: '{text}'", developer_message="", duration=0.0)
            
        driver = WindowsDriver()
        executor = ActionExecutor(driver)
        
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
            
            target_handle = win_handle
            if element_name:
                el_handle = driver.find_element(win_handle, None, element_name)
                if el_handle:
                    target_handle = el_handle
            
            result = executor.type_text(target_handle, text, clear_first)
            
            if result.success and context and getattr(context, "automation", None):
                context.automation.session.last_action = "TYPE"
                context.automation.add_recent_element(target_handle.ui_element)
                
            return ToolResult(
                tool_name=self.name,
                success=result.success,
                user_message=f"Typed '{text}'.",
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
