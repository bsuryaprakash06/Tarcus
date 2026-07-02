import os
from datetime import datetime
from PIL import ImageGrab
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ToolResult, ExecutionContext
from src.utils.settings import DRY_RUN

class TakeScreenshotTool(BaseTool):
    
    @property
    def name(self) -> str:
        return "take_screenshot"

    @property
    def description(self) -> str:
        return "Captures a screenshot of the current desktop and saves it to a file."

    @property
    def arguments_schema(self) -> dict:
        return {}

    @property
    def examples(self) -> list[str]:
        return [
            "take a screenshot",
            "capture my screen",
            "take screenshot"
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
                message="[DRY RUN] Screenshot would be captured and saved here.",
                duration=0.0
            )

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            exec_id = context.execution_id if context else "no_id"
            
            output_dir = os.path.join(os.getcwd(), "assets", "screenshots")
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{timestamp}_{exec_id}.png"
            output_path = os.path.join(output_dir, filename)
            
            screenshot = ImageGrab.grab()
            screenshot.save(output_path, "PNG")
            
            return ToolResult(
                tool_name=self.name,
                success=True,
                message=f"Screenshot saved successfully to {output_path}",
                duration=0.0
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                message=f"Failed to capture screenshot: {str(e)}",
                duration=0.0
            )
