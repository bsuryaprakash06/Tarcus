import pyperclip
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.utils.settings import DRY_RUN

class ReadClipboardTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "read_clipboard"

    @property
    def description(self) -> str:
        return "Reads the current text content of the system clipboard."

    @property
    def arguments_schema(self) -> dict:
        return {}

    @property
    def examples(self) -> list[str]:
        return [
            "what's on my clipboard?",
            "read clipboard",
            "get clipboard contents"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.SAFE

    @property
    def category(self) -> str:
        return "System"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                message="[DRY RUN] Would read contents from clipboard.",
                duration=0.0
            )

        try:
            content = pyperclip.paste()
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"Clipboard read successfully.",
                duration=0.0,
                data={"clipboard_content": content}
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to read clipboard: {str(e)}",
                duration=0.0
            )
