import os
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
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
                message=f"[DRY RUN] Would delete file '{file_path}'.",
                duration=0.0
            )

        try:
            os.remove(file_path)
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"Successfully deleted {file_path}",
                duration=0.0
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to delete file: {str(e)}",
                duration=0.0
            )
