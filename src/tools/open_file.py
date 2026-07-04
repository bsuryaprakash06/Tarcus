import os
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.models.error_codes import ErrorCode
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
                user_message="I'm missing some required information.",
                    developer_message="File path must be provided.",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    duration=0.0
            )
            
        if not os.path.isabs(file_path) and context:
            file_path = os.path.join(context.cwd, file_path)
            
        if not os.path.exists(file_path):
            return ToolResult(
                tool_name=self.name,
                success=False,
                user_message="I couldn't complete that action.",
                    developer_message=f"File not found: {file_path}",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    duration=0.0
            )
            
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=f"Simulating open file: {file_path}",
                    developer_message=f"[DRY RUN] Would open file: {file_path}",
                    duration=0.0
            )

        try:
            os.startfile(file_path)
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message="Opened the requested item.",
                    developer_message=f"Successfully opened {file_path}",
                    duration=0.0
            )
        except Exception as e:
            return self.error_result(e)
