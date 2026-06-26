from src.tools.base_tool import BaseTool
from src.tools.open_application import OpenApplicationTool
from src.tools.create_folder import CreateFolderTool
from src.tools.search_web import SearchWebTool

class ToolRegistry:
    """Manages registration and lookup of available tools."""
    
    def __init__(self):
        self._tools = {}
        # Auto-register core tools
        self.register(OpenApplicationTool())
        self.register(CreateFolderTool())
        self.register(SearchWebTool())

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())
