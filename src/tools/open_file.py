import os
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.utils.settings import DRY_RUN

class OpenFileTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "open_file"

    @property
    def description(self) -> str:
        return "Opens a file using its default associated application."

    @property
    def arguments_schema(self) -> dict:
        return {
            "file_path": {
                "type": "string",
                "description": "Absolute or relative path to the file to open."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "open report.pdf",
            "launch the image file",
            "open document.docx"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.SAFE

    @property
    def category(self) -> str:
        return "Files"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        file_path = arguments.get("file_path", "")
        if not file_path:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message="File path must be provided.",
                duration=0.0
            )
            
        if not os.path.isabs(file_path) and context:
            file_path = os.path.join(context.cwd, file_path)
            
        if not os.path.exists(file_path):
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"File not found: {file_path}",
                duration=0.0
            )
            
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"[DRY RUN] Would open file: {file_path}",
                duration=0.0
            )

        try:
            os.startfile(file_path)
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"Successfully opened {file_path}",
                duration=0.0
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to open file: {str(e)}",
                duration=0.0
            )
