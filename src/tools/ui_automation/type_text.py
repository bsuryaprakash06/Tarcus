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
            "text": {
                "type": "string",
                "description": "The text to type."
            },
            "element_name": {
                "type": "string",
                "optional": True,
                "description": "Optional. The name of the element to type into."
            },
            "clear_first": {
                "type": "boolean",
                "optional": True,
                "description": "Boolean indicating whether to clear the field first (default false)."
            }
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
            
        clear_first = arguments.get("clear_first", False)
        
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"[DRY RUN] Would type: '{text}'", developer_message="", duration=0.0)
            
        start_time = time.time()
        try:
            # 1. Grab Universal Context
            interaction = context.interaction if context else None
            if not interaction or not interaction.current_target:
                return ToolResult(tool_name=self.name, success=False, user_message="No active target to type into.", developer_message="InteractionContext missing or empty", duration=0.0)
                
            # 2. Check Target Capability dynamically
            from src.models.target import TargetCapability
            if not interaction.current_target.can(TargetCapability.TYPING):
                return ToolResult(tool_name=self.name, success=False, user_message="There isn't an editable text field in the current target.", developer_message=f"Target {interaction.current_target.id} lacks TYPING capability", duration=0.0)
                
            # 3. Use abstract Backend and FocusManager
            from src.automation.windows_driver import WindowsDriver
            from src.automation.focus_manager import FocusManager
            
            # TODO: The handler will inject the correct backend (Windows, Mac, Browser). We hardcode for now.
            backend = WindowsDriver() 
            focus_manager = FocusManager(backend)
            
            if not focus_manager.prepare_for_interaction(interaction, TargetCapability.TYPING):
                return ToolResult(tool_name=self.name, success=False, user_message="Failed to focus the target element.", developer_message="FocusManager rejected interaction", duration=0.0)
                
            success = backend.type_text(interaction, text, clear_first)
            
            return ToolResult(
                tool_name=self.name,
                success=success,
                user_message=f"Typed '{text}'.",
                developer_message="",
                duration=time.time() - start_time
            )
        except Exception as e:
            return self.error_result(e)
