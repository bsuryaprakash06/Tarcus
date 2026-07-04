import subprocess
import time
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.models.error_codes import ErrorCode
from src.utils.logger import get_logger

logger = get_logger("tool.open_application")

from src.utils.settings import DRY_RUN

class OpenApplicationTool(BaseTool):
    @property
    def name(self) -> str:
        return "open_application"

    @property
    def description(self) -> str:
        return "Launches a Windows application by name."

    @property
    def arguments_schema(self) -> dict:
        return {
            "application": {
                "type": "string",
                "description": "Name of the application executable to run (without path or extension, e.g. 'notepad', 'calc')."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "Open Notepad",
            "Launch Calculator",
            "Start Paint",
            "Open cmd"
        ]

    @property
    def category(self) -> str:
        return "System"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        start_time = time.time()
        app_name = arguments.get("application", "").strip()
        if not app_name:
            duration = time.time() - start_time
            return ToolResult(tool_name=self.name, success=False, user_message="I need to know which application to open.", developer_message="Application name argument is missing or empty.", error_code=ErrorCode.VALIDATION_ERROR, duration=duration)
            
        logger.info(f"Executing open_application for: '{app_name}'")
        
        # Security sanitization check: app_name should be only alphanumeric
        if not app_name.isalnum():
            duration = time.time() - start_time
            return ToolResult(tool_name=self.name, success=False, user_message="That doesn't look like a valid application name.", developer_message=f"Invalid application name format: '{app_name}'", error_code=ErrorCode.VALIDATION_ERROR, duration=duration)

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would open application: {app_name}")
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=f"Simulating opening {app_name}.",
                developer_message=f"Would open {app_name}.",
                duration=time.time() - start_time,
                data={"application": app_name, "dry_run": True}
            )

        try:
            # We use subprocess.Popen with shell=True under Windows to support detaching launched GUI apps
            subprocess.Popen(f"start {app_name}", shell=True)
            duration = time.time() - start_time
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=f"Opening {app_name}.",
                developer_message=f"I have opened {app_name}.",
                duration=duration,
                data={"application": app_name}
            )
        except Exception as e:
            logger.error(f"Failed to launch application {app_name}: {e}")
            res = self.error_result(e)
            res.duration = time.time() - start_time
            return res
