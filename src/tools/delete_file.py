import os
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.models.error_codes import ErrorCode
from src.utils.settings import DRY_RUN

class DeleteFileTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "delete_file"

    @property
    def description(self) -> str:
        return "Deletes a file permanently from the filesystem."

    @property
    def arguments_schema(self) -> dict:
        return {
            "file_path": {
                "type": "string",
                "description": "The path of the file to delete."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "delete report.txt",
            "remove the temp file"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.CONFIRM

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
                user_message=f"Simulating delete file '{file_path}'.",
                    developer_message=f"[DRY RUN] Would delete file '{file_path}'.",
                    duration=0.0
            )

        try:
            os.remove(file_path)
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message="Deleted successfully.",
                    developer_message=f"Successfully deleted {file_path}",
                    duration=0.0
            )
        except Exception as e:
            return self.error_result(e)
