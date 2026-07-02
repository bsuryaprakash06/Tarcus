import os
import shutil
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.utils.settings import DRY_RUN

class MoveFileTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "move_file"

    @property
    def description(self) -> str:
        return "Moves a file to a new directory."

    @property
    def arguments_schema(self) -> dict:
        return {
            "source_path": {
                "type": "string",
                "description": "The current path of the file."
            },
            "destination_dir": {
                "type": "string",
                "description": "The target directory to move the file to."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "move report.txt to the documents folder",
            "put this file in my downloads"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.CONFIRM

    @property
    def category(self) -> str:
        return "Files"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        source_path = arguments.get("source_path", "")
        destination_dir = arguments.get("destination_dir", "")
        
        if not source_path or not destination_dir:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message="Both source_path and destination_dir must be provided.",
                duration=0.0
            )
            
        if not os.path.isabs(source_path) and context:
            source_path = os.path.join(context.cwd, source_path)
            
        if not os.path.isabs(destination_dir) and context:
            destination_dir = os.path.join(context.cwd, destination_dir)
            
        if not os.path.exists(source_path):
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Source file not found: {source_path}",
                duration=0.0
            )
            
        os.makedirs(destination_dir, exist_ok=True)
        target_path = os.path.join(destination_dir, os.path.basename(source_path))
            
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"[DRY RUN] Would move '{source_path}' to '{target_path}'.",
                duration=0.0
            )

        try:
            shutil.move(source_path, target_path)
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"Successfully moved to {target_path}",
                duration=0.0
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to move file: {str(e)}",
                duration=0.0
            )
