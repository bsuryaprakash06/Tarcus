import os
import time
from pathlib import Path
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.utils.logger import get_logger

logger = get_logger("tool.create_folder")

class CreateFolderTool(BaseTool):
    @property
    def name(self) -> str:
        return "create_folder"

    @property
    def description(self) -> str:
        return "Creates a new folder at an abstract location (such as 'documents' or 'root')."

    @property
    def arguments_schema(self) -> dict:
        return {
            "name": {
                "type": "string",
                "description": "Name of the folder to create."
            },
            "location": {
                "type": "string",
                "enum": ["documents", "root"],
                "description": "Abstract target folder location. Supported values: 'documents' (maps to the workspace documents directory), 'root' (maps to project root)."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "Create a folder named physics",
            "Make a new directory called coding",
            "Create folder music in root"
        ]

    @property
    def category(self) -> str:
        return "Files"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        start_time = time.time()
        folder_name = arguments.get("name", "").strip()
        location_key = arguments.get("location", "documents").strip().lower()
        
        if not folder_name:
            duration = time.time() - start_time
            return ToolResult(tool_name=self.name, success=False, message="Folder name argument is missing or empty.", duration=duration)

        # Resolve abstract location using the current execution context path (or fallback to context.cwd or os.getcwd())
        cwd = context.cwd if context else os.getcwd()
        base_path = Path(cwd)
        if location_key != "root":
            base_path = base_path.parent

        target_path = base_path / folder_name
        
        logger.info(f"Executing create_folder: '{folder_name}' in base path: '{base_path}'")
        
        try:
            # Security verification: prevent path traversal
            real_base = os.path.abspath(base_path)
            real_target = os.path.abspath(target_path)
            if not real_target.startswith(real_base):
                duration = time.time() - start_time
                return ToolResult(tool_name=self.name, success=False, message="Security Error: Directory traversal attempt detected.", duration=duration)
                
            target_path.mkdir(parents=True, exist_ok=True)
            duration = time.time() - start_time
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"I have created the folder {folder_name}.",
                duration=duration,
                data={"path": str(target_path)}
            )
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            duration = time.time() - start_time
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to create folder {folder_name}: {e}",
                duration=duration
            )
