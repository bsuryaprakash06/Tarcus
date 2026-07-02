from datetime import datetime
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext

class GetCurrentTimeTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "get_current_time"

    @property
    def description(self) -> str:
        return "Returns the current local date and time."

    @property
    def arguments_schema(self) -> dict:
        return {}

    @property
    def examples(self) -> list[str]:
        return [
            "what time is it?",
            "what is today's date?",
            "current time"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.SAFE

    @property
    def category(self) -> str:
        return "System"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        return ToolResult(
            tool_name=self.name,
            success=True,
            message=f"The current local date and time is {current_time}",
            duration=0.0
        )
