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
        double = arguments.get("double_click", False)
        right = arguments.get("right_click", False)
        
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"[DRY RUN] Would click element: {element_name}", developer_message="", duration=0.0)
            
        start_time = time.time()
        try:
            interaction = context.interaction if context else None
            if not interaction or not interaction.current_target:
                return ToolResult(tool_name=self.name, success=False, user_message="No active target to click.", developer_message="InteractionContext missing or empty", duration=0.0)
                
            from src.models.target import TargetCapability
            if not interaction.current_target.can(TargetCapability.CLICKING):
                return ToolResult(tool_name=self.name, success=False, user_message="The current target does not support clicking.", developer_message=f"Target lacks CLICKING capability", duration=0.0)
                
            from src.automation.windows_driver import WindowsDriver
            from src.automation.focus_manager import FocusManager
            
            backend = WindowsDriver() 
            focus_manager = FocusManager(backend)
            
            # Find the element specifically
            if element_name and element_name.lower() not in ("it", "that", "this", "them"):
                el_handle = backend.find_element(interaction, element_name)
                if not el_handle:
                    return ToolResult(tool_name=self.name, success=False, user_message=f"Could not find element: {element_name}", developer_message="Locator returned None", duration=0.0)
                interaction.focused_element = el_handle.ui_element
            elif not interaction.focused_element:
                return ToolResult(tool_name=self.name, success=False, user_message="I don't know what to click.", developer_message="No element specified and no prior context", duration=0.0)
            
            if not focus_manager.prepare_for_interaction(interaction, TargetCapability.CLICKING):
                return ToolResult(tool_name=self.name, success=False, user_message="Failed to focus the target element.", developer_message="FocusManager rejected interaction", duration=0.0)
                
            success = backend.click(interaction, double, right)
            
            return ToolResult(
                tool_name=self.name,
                success=success,
                user_message=f"Clicked '{element_name or 'the item'}'.",
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
