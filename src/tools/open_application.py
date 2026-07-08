import subprocess
import time
from src.tools.base_tool import BaseTool
from src.models.plan import ToolResult, ExecutionContext
from src.models.error_codes import ErrorCode
from src.utils.logger import get_logger
from src.utils.settings import DRY_RUN

from src.models.verification import ToolMetadata, RecoveryPolicy, RecoveryStrategy

logger = get_logger("tool.open_application")

class OpenApplicationTool(BaseTool):
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            tool_name=self.name,
            verification_rules=["window_exists"], # In future: ["process_running", "window_exists"]
            recovery_policy=RecoveryPolicy(
                strategies=[
                    RecoveryStrategy.RETRY
                ]
            ),
            timeout_sec=15.0
        )
        
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
            return ToolResult(tool_name=self.name, success=False, user_message="I need to know which application to open.", developer_message="Missing argument.", error_code=ErrorCode.VALIDATION_ERROR, duration=time.time() - start_time)
            
        logger.info(f"Executing open_application for: '{app_name}'")
        
        if not app_name.isalnum():
            return ToolResult(tool_name=self.name, success=False, user_message="Invalid name.", developer_message=f"Invalid format: '{app_name}'", error_code=ErrorCode.VALIDATION_ERROR, duration=time.time() - start_time)

        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message=f"Simulating opening {app_name}.", developer_message="Dry run successful", duration=time.time() - start_time)

        try:
            # Launch
            subprocess.Popen(f"start {app_name}", shell=True)
            
            # Wait a tiny bit for the process to register its main window
            time.sleep(1.0)
            
            # Trigger Platform Discovery & Registration
            from src.automation.windows_driver import WindowsDriver
            from src.automation.interaction_manager import InteractionManager
            
            driver = WindowsDriver()
            manager = InteractionManager()
            manager.discover_and_sync(driver) # Populates Registry and Sessions
            
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=f"Opening {app_name}.",
                developer_message=f"I have opened {app_name}.",
                duration=time.time() - start_time,
                data={"application": app_name}
            )
        except Exception as e:
            logger.error(f"Failed to launch application {app_name}: {e}")
            res = self.error_result(e)
            res.duration = time.time() - start_time
            return res
