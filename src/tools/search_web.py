import webbrowser
import time
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.utils.logger import get_logger

logger = get_logger("tool.search_web")

from src.utils.settings import DRY_RUN

class SearchWebTool(BaseTool):
    @property
    def name(self) -> str:
        return "search_web"

    @property
    def description(self) -> str:
        return "Searches the web for a given query string using the default browser."

    @property
    def arguments_schema(self) -> dict:
        return {
            "query": {
                "type": "string",
                "description": "The search query query string."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "Search Google for python programming",
            "Search the web for weather in New York",
            "Google Ollama setup guide"
        ]

    @property
    def category(self) -> str:
        return "Browser"

    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        start_time = time.time()
        query = arguments.get("query", "").strip()
        if not query:
            duration = time.time() - start_time
            return ToolResult(tool_name=self.name, success=False, message="Search query argument is missing or empty.", duration=duration)
            
        logger.info(f"Executing search_web for query: '{query}'")
        
        try:
            # Construct Google search URL
            url = f"https://www.google.com/search?q={query}"
            
            if DRY_RUN:
                logger.info(f"[DRY RUN] Would search the web for: {query}")
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    message=f"Would search the web for {query}.",
                    duration=time.time() - start_time,
                    data={"query": query, "url": url, "dry_run": True}
                )

            webbrowser.open(url)
            duration = time.time() - start_time
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"I have searched the web for {query}.",
                duration=duration,
                data={"query": query, "url": url}
            )
        except Exception as e:
            logger.error(f"Failed to search web: {e}")
            duration = time.time() - start_time
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to search the web: {e}",
                duration=duration
            )
