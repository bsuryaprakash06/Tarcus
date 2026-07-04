import psutil
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.models.error_codes import ErrorCode
from src.utils.settings import DRY_RUN

class CloseApplicationTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "close_application"

    @property
    def description(self) -> str:
        return "Closes a running application by its process name."

    @property
    def arguments_schema(self) -> dict:
        return {
            "application": {
                "type": "string",
                "description": "The name of the application to close (e.g. 'notepad', 'chrome')."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "close notepad",
            "terminate chrome",
            "quit Spotify"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.CONFIRM

    @property
    def category(self) -> str:
        return "System"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        app_name = arguments.get("application", "").lower()
        
        if not app_name:
            return ToolResult(
                tool_name=self.name,
                success=False,
                user_message="I'm missing some required information.",
                    developer_message="Application name must be provided.",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    duration=0.0
            )
            
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=f"Simulating attempt to terminate process matching '{app_name}'.",
                    developer_message=f"[DRY RUN] Would attempt to terminate process matching '{app_name}'.",
                    duration=0.0
            )

        terminated_count = 0
        try:
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info.get('name', '')
                if proc_name and app_name in proc_name.lower():
                    proc.terminate()
                    terminated_count += 1
            
            if terminated_count > 0:
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    user_message="Action completed successfully.",
                    developer_message=f"Successfully sent termination signal to {terminated_count} process(es) matching '{app_name}'.",
                    duration=0.0
                )
            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    user_message="I couldn't complete that action.",
                    developer_message=f"No running processes found matching '{app_name}'.",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    duration=0.0
                )
        except Exception as e:
            return self.error_result(e)
