import importlib
import pkgutil
import inspect
from pathlib import Path
from src.tools.base_tool import BaseTool
from src.utils.logger import get_logger

logger = get_logger("tools.registry")

class ToolRegistry:
    """Manages registration and automatic discovery of available tools."""
    
    def __init__(self):
        self._tools = {}
        self._discover_and_register_tools()

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name} (v{tool.version})")

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def _discover_and_register_tools(self) -> None:
        """
        Dynamically discovers and registers all BaseTool subclasses
        defined in modules within the src.tools package and subpackages.
        """
        import src.tools
        package_dir = str(Path(__file__).parent)
        
        for _, module_name, is_pkg in pkgutil.walk_packages([package_dir], prefix="src.tools."):
            if module_name.endswith("base_tool") or module_name.endswith("registry") or module_name.endswith("__init__"):
                continue
                
            try:
                module = importlib.import_module(module_name)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseTool) and obj is not BaseTool:
                        try:
                            # Instantiate and register the discovered tool
                            self.register(obj())
                        except Exception as e:
                            logger.error(f"Failed to instantiate tool class {name}: {e}")
            except Exception as e:
                logger.error(f"Failed to import tool module {module_name}: {e}")
