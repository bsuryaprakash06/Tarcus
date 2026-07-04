from abc import ABC, abstractmethod
from enum import Enum
from src.models.plan import ToolResult, ExecutionContext

class SafetyLevel(Enum):
    SAFE = "SAFE"
    CONFIRM = "CONFIRM"
    RESTRICTED = "RESTRICTED"
    BLOCKED = "BLOCKED"

class BaseTool(ABC):
    """Abstract base class representing a tool that can be executed by the assistant."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of the tool's purpose and usage."""
        pass

    @property
    @abstractmethod
    def arguments_schema(self) -> dict:
        """Schema describing arguments and types expected by the tool."""
        pass

    @property
    @abstractmethod
    def examples(self) -> list[str]:
        """A list of sample user query phrases that would trigger this tool."""
        pass

    @property
    def safety_level(self) -> SafetyLevel:
        """Safety classification of the tool. Defaults to SAFE."""
        return SafetyLevel.SAFE

    @property
    def version(self) -> str:
        """Version of the tool. Defaults to '1.0'."""
        return "1.0"

    @property
    @abstractmethod
    def category(self) -> str:
        """Category category the tool belongs to (e.g. 'System', 'Browser', 'Files')."""
        pass

    @abstractmethod
    def execute(self, arguments: dict, context: ExecutionContext = None) -> ToolResult:
        """Executes the tool with the given arguments and optional context."""
        pass
        
    def error_result(self, exception: Exception) -> ToolResult:
        """Helper to safely map internal exceptions to a standard ToolResult."""
        # Import inside the method or at the top
        from src.services.error_mapper import ErrorMapper
        mapped = ErrorMapper.to_user_message(exception)
        return ToolResult(
            tool_name=self.name,
            success=False,
            user_message=mapped.user_message,
            developer_message=str(exception),
            error_code=mapped.error_code,
            duration=0.0
        )
