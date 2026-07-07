import time
from src.tools.base_tool import BaseTool
from src.models.plan import ToolResult
from src.models.error_codes import ErrorCode
from src.models.target import TargetSession
from src.automation.windows_driver import WindowsDriver
from src.utils.logger import get_logger
from src.utils.settings import DRY_RUN

logger = get_logger("tool.type_text")

class TypeTextTool(BaseTool):
    @property
    def name(self) -> str:
        return "type_text"

    @property
    def description(self) -> str:
        return "Types text into the specific provided target session."

    @property
    def arguments_schema(self) -> dict:
        return {
            "text": {
                "type": "string",
                "description": "The exact text to type."
            },
            "clear_first": {
                "type": "boolean",
                "description": "Whether to clear the field before typing. Default is false."
            }
        }

    @property
    def examples(self) -> list[str]:
        return [
            "Type Hello Shane"
        ]

    @property
    def category(self) -> str:
        return "UI Automation"

    def execute(self, arguments: dict, context: TargetSession = None) -> ToolResult:
        start_time = time.time()
        text = arguments.get("text", "")
        clear_first = arguments.get("clear_first", False)
        
        if not text:
            return ToolResult(tool_name=self.name, success=False, user_message="I need text.", developer_message="Missing text.", error_code=ErrorCode.VALIDATION_ERROR, duration=time.time() - start_time)

        if not context or not isinstance(context, TargetSession):
            return ToolResult(tool_name=self.name, success=False, user_message="I lost focus of the target.", developer_message="Missing TargetSession context.", error_code=ErrorCode.EXECUTION_FAILED, duration=time.time() - start_time)

        logger.info(f"Executing type_text '{text}' into target {context.target.id}")
        
        if DRY_RUN:
            return ToolResult(tool_name=self.name, success=True, user_message="Simulating typing.", developer_message="Dry run successful", duration=time.time() - start_time)

        try:
            driver = WindowsDriver()
            success = driver.type(context, text, clear_first)
            
            duration = time.time() - start_time
            if success:
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    user_message=f"I typed the text.",
                    developer_message=f"Typed text into {context.target.id}",
                    duration=duration
                )
            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    user_message="I couldn't type into the window.",
                    developer_message=f"Driver type() failed for {context.target.id}",
                    error_code=ErrorCode.EXECUTION_FAILED,
                    duration=duration
                )
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            res = self.error_result(e)
            res.duration = time.time() - start_time
            return res
