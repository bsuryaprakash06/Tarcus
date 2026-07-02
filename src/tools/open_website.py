import webbrowser
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
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
                message="A URL must be provided.",
                duration=0.0
            )

        # Ensure scheme
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
            
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"[DRY RUN] Would open browser to {url}",
                duration=0.0
            )

        try:
            webbrowser.open(url)
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"Successfully opened {url} in the default browser.",
                duration=0.0
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to open URL: {str(e)}",
                duration=0.0
            )
