import time
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.automation.windows_driver import WindowsDriver
from src.automation.action_executor import ActionExecutor
from src.utils.settings import DRY_RUN

class ClickElementTool(BaseTool):
    @property
    def name(self) -> str:
        return "click_element"
        
    @property
    def description(self) -> str:
        return "Clicks a specific UI element (e.g. button, menu item, checkbox) within the currently focused window."
        
    @property
    def arguments_schema(self) -> dict:
        return {
            "element_name": {
                "type": "string",
                "description": "The name or text of the element to click."
            },
            "double_click": {
                "type": "boolean",
                "optional": True,
                "description": "Boolean indicating if it should be a double click (default false)."
            },
            "right_click": {
                "type": "boolean",
                "optional": True,
                "description": "Boolean indicating if it should be a right click (default false)."
            }
        }
        
    @property
    def examples(self) -> list[str]:
        return ["Click the Save button", "Click it again", "Double click the file"]
        
    @property
    def category(self) -> str:
        return "UI Automation"
        
    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        element_name = arguments.get("element_name")
        if not element_name and not (context and context.automation.recent_elements):
            return ToolResult(tool_name=self.name, success=False, user_message="Missing element name.", developer_message="Missing arg: element_name", duration=0.0)
            
        double = arguments.get("double_click", False)
        right = arguments.get("right_click", False)
        
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"[DRY RUN] Would click element: {element_name}", developer_message="", duration=0.0)
            
        driver = WindowsDriver()
        executor = ActionExecutor(driver)
        
        start_time = time.time()
        try:
            active_window_name = context.automation.session.active_window if context and getattr(context, "automation", None) else None
            if not active_window_name:
                # Fallback to foreground window
                from src.automation.window_manager import WindowManager
                active_window_name = WindowManager.get_foreground_window()
                
            if not active_window_name:
                return ToolResult(tool_name=self.name, success=False, user_message="No active window to click inside.", developer_message="active_window is None", duration=0.0)
                
            win_handle = driver.find_window(active_window_name)
            if not win_handle:
                return ToolResult(tool_name=self.name, success=False, user_message="Active window lost.", developer_message="", duration=0.0)
            
            # Resolve Handle (Handle Pronoun "it" vs Named)
            el_handle = None
            if element_name and element_name.lower() in ("it", "that", "this", "them"):
                if context and context.automation.recent_elements:
                    recent = context.automation.recent_elements[0] # Just need the name to re-search, or we'd ideally cache the actual handle. For now, search by name again to be safe.
                    el_handle = driver.find_element(win_handle, None, recent.name)
            else:
                el_handle = driver.find_element(win_handle, None, element_name)
                
            if not el_handle:
                return ToolResult(tool_name=self.name, success=False, user_message=f"Could not find element: {element_name}", developer_message="Locator returned None", duration=0.0)
            
            result = executor.click(el_handle, double, right)
            
            if result.success and context and getattr(context, "automation", None):
                context.automation.session.last_locator = element_name
                context.automation.session.last_action = "CLICK"
                context.automation.add_recent_element(el_handle.ui_element)
                
            return ToolResult(
                tool_name=self.name,
                success=result.success,
                user_message=f"Clicked '{element_name}'.",
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
