import psutil
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.utils.settings import DRY_RUN

class ListRunningApplicationsTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "list_running_applications"

    @property
    def description(self) -> str:
        return "Returns a list of active applications and their process names."

    @property
    def arguments_schema(self) -> dict:
        return {}

    @property
    def examples(self) -> list[str]:
        return [
            "what applications are running?",
            "list running apps"
        ]

    @property
    def safety_level(self) -> SafetyLevel:
        return SafetyLevel.SAFE

    @property
    def category(self) -> str:
        return "System"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        if DRY_RUN:
            return ToolResult(
                tool_name=self.name,
                success=True,
                message="[DRY RUN] Would list running applications.",
                duration=0.0
            )

        try:
            apps = set()
            for proc in psutil.process_iter(['name']):
                name = proc.info.get('name')
                if name:
                    # Filter out purely system processes for user relevance (basic heuristic)
                    if not name.lower().startswith(('svchost', 'system', 'registry', 'smss')):
                        apps.add(name)
            
            app_list_str = "\n".join(sorted(apps))
            
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"Running applications:\n{app_list_str}",
                duration=0.0,
                data={"applications": list(apps)}
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to list applications: {str(e)}",
                duration=0.0
            )
