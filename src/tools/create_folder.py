import os
import time
from pathlib import Path
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.models.error_codes import ErrorCode
from src.utils.logger import get_logger

logger = get_logger("tool.create_folder")

from src.utils.settings import DRY_RUN

class CreateFolderTool(BaseTool):
    @property
    def name(self) -> str:
        return "create_folder"

    @property
    def description(self) -> str:
        return "Creates a new directory/folder at the specified logical location."

    @property
    def arguments_schema(self) -> dict:
        return {
            "name": {
                "type": "string",
                "description": "The name of the folder to create."
            },
            "location": {
                "type": "string",
                "enum": ["documents", "root"],
                "description": "The logical location where the folder should be created."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "Create a folder named physics",
            "Make a new directory for my project",
            "Create folder called test"
        ]

    @property
    def category(self) -> str:
        return "Files"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        start_time = time.time()
        folder_name = arguments.get("name", "").strip()
        location_key = arguments.get("location", "root").lower()
        
        if not folder_name:
            duration = time.time() - start_time
            return ToolResult(tool_name=self.name, success=False, user_message="I need to know the name of the folder.", developer_message="Folder name argument is missing or empty.", error_code=ErrorCode.VALIDATION_ERROR, duration=duration)

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
                return ToolResult(tool_name=self.name, success=False, user_message="I cannot create a folder outside the allowed directory.", developer_message="Security Error: Directory traversal attempt detected.", error_code=ErrorCode.PERMISSION_DENIED, duration=duration)
                
            if DRY_RUN:
                logger.info(f"[DRY RUN] Would create folder: {target_path}")
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    user_message=f"Simulating creating the folder {folder_name}.",
                    developer_message=f"Would create the folder {folder_name}.",
                    duration=time.time() - start_time,
                    data={"path": str(target_path), "dry_run": True}
                )

            target_path.mkdir(parents=True, exist_ok=True)
            duration = time.time() - start_time
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=f"Created the folder {folder_name}.",
                developer_message=f"I have created the folder {folder_name}.",
                duration=duration,
                data={"path": str(target_path)}
            )
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            res = self.error_result(e)
            res.duration = time.time() - start_time
            return res
