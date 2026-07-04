import webbrowser
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.models.error_codes import ErrorCode
from src.utils.settings import DRY_RUN

class OpenWebsiteTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "open_website"

    @property
    def description(self) -> str:
        return "Opens a specific URL in the default web browser."

    @property
    def arguments_schema(self) -> dict:
        return {
            "url": {
                "type": "string",
                "description": "The full URL to open (e.g. 'https://www.google.com')"
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "open google",
            "go to youtube",
            "navigate to github"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.SAFE

    @property
    def category(self) -> str:
        return "Browser"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        url = arguments.get("url")
        if not url:
            return ToolResult(
                tool_name=self.name,
                success=False,
                user_message="I'm missing some required information.",
                    developer_message="A URL must be provided.",
                    error_code=ErrorCode.VALIDATION_ERROR,
                    duration=0.0
            )

        # Ensure scheme
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
            
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message=f"Simulating open browser to {url}",
                    developer_message=f"[DRY RUN] Would open browser to {url}",
                    duration=0.0
            )

        try:
            webbrowser.open(url)
            return ToolResult(
                tool_name=self.name,
                success=True,
                user_message="Opened the requested item.",
                    developer_message=f"Successfully opened {url} in the default browser.",
                    duration=0.0
            )
        except Exception as e:
            return self.error_result(e)
