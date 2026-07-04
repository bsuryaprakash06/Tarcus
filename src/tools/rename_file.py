import os
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.models.error_codes import ErrorCode
from src.utils.settings import DRY_RUN

class RenameFileTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "rename_file"

    @property
    def description(self) -> str:
        return "Renames a file on the filesystem."

    @property
    def arguments_schema(self) -> dict:
        return {
            "source_path": {
                "type": "string",
                "description": "The current path of the file."
            },
            "new_name": {
                "type": "string",
                "description": "The new name (or relative path) for the file."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "rename report.txt to final_report.txt",
            "change the name of image.png to avatar.png"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.CONFIRM

    @property
    def category(self) -> str:
        return "Files"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        source_path = arguments.get("source_path", "")
        new_name = arguments.get("new_name", "")
        
        if not source_path or not new_name:
            return ToolResult(
                tool_name=self.name,
                success=False,
                user_message="I'm missing some required information.",
                    developer_message="Both source_path and new_name must be provided.",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    duration=0.0
            )
            
        if not os.path.isabs(source_path) and context:
            source_path = os.path.join(context.cwd, source_path)
            
        if not os.path.exists(source_path):
            return ToolResult(
                tool_name=self.name,
                success=False,
                user_message="I couldn't complete that action.",
                    developer_message=f"Source file not found: {source_path}",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    duration=0.0
            )
            
        # Determine target path
        target_dir = os.path.dirname(source_path)
        target_path = os.path.join(target_dir, new_name)
            
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=f"Simulating rename '{source_path}' to '{target_path}'.",
                    developer_message=f"[DRY RUN] Would rename '{source_path}' to '{target_path}'.",
                    duration=0.0
            )

        try:
            os.rename(source_path, target_path)
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message="Renamed successfully.",
                    developer_message=f"Successfully renamed to {target_path}",
                    duration=0.0
            )
        except Exception as e:
            return self.error_result(e)
