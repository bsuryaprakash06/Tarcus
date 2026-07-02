import pyperclip
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.utils.settings import DRY_RUN

class CopyClipboardTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "copy_clipboard"

    @property
    def description(self) -> str:
        return "Copies provided text to the system clipboard."

    @property
    def arguments_schema(self) -> dict:
        return {
            "text": {
                "type": "string",
                "description": "The text to copy to the clipboard."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "copy 'hello world' to clipboard",
            "put this on my clipboard"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.SAFE

    @property
    def category(self) -> str:
        return "System"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        text = arguments.get("text")
        if text is None:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message="Text argument must be provided.",
                duration=0.0
            )
            
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"[DRY RUN] Would copy '{text}' to clipboard.",
                duration=0.0
            )

        try:
            pyperclip.copy(text)
            return ToolResult(
                tool_name=self.name,
                success=True,
                message="Text successfully copied to clipboard.",
                duration=0.0
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to copy to clipboard: {str(e)}",
                duration=0.0
            )
