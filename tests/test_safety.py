import unittest
from src.safety.validator import SafetyValidator, SafetyError
from src.tools.registry import ToolRegistry
from src.tools.base_tool import BaseTool, SafetyLevel
from src.models.plan import ExecutionPlan, PlanItem, ExecutionContext, ToolResult

class SafetyMockTool(BaseTool):
    def __init__(self, name: str, safety_level: SafetyLevel):
        self._name = name
        self._safety_level = safety_level

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return "Mock tool for safety testing."

    @property
    def arguments_schema(self) -> dict:
        return {}

    @property
    def examples(self) -> list[str]:
        return []

    @property
    def category(self) -> str:
        return "Test"

    @property
    def safety_level(self) -> SafetyLevel:
        return self._safety_level

    def execute(self, arguments: dict, context: ExecutionContext) -> ToolResult:
        return ToolResult(tool_name=self.name, success=True, message="Executed", duration=0.0)

class TestSafety(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        
        # Create tools with different safety levels
        self.safe_tool = SafetyMockTool("safe_tool", SafetyLevel.SAFE)
        self.confirm_tool = SafetyMockTool("confirm_tool", SafetyLevel.CONFIRM)
        self.restricted_tool = SafetyMockTool("restricted_tool", SafetyLevel.RESTRICTED)
        self.blocked_tool = SafetyMockTool("blocked_tool", SafetyLevel.BLOCKED)
        
        self.registry.register(self.safe_tool)
        self.registry.register(self.confirm_tool)
        self.registry.register(self.restricted_tool)
        self.registry.register(self.blocked_tool)
        
        self.validator = SafetyValidator(tool_registry=self.registry)

    def test_validate_plan_all_safe(self):
        plan = ExecutionPlan(plan=[
            PlanItem(tool="safe_tool", arguments={})
        ])
        needs_confirm = self.validator.validate_plan(plan)
        self.assertFalse(needs_confirm)

    def test_validate_plan_needs_confirm(self):
        plan = ExecutionPlan(plan=[
            PlanItem(tool="safe_tool", arguments={}),
            PlanItem(tool="confirm_tool", arguments={})
        ])
        needs_confirm = self.validator.validate_plan(plan)
        self.assertTrue(needs_confirm)

    def test_validate_plan_restricted(self):
        plan = ExecutionPlan(plan=[
            PlanItem(tool="restricted_tool", arguments={})
        ])
        with self.assertRaises(SafetyError) as context:
            self.validator.validate_plan(plan)
        self.assertIn("restricted", str(context.exception))

    def test_validate_plan_blocked(self):
        plan = ExecutionPlan(plan=[
            PlanItem(tool="blocked_tool", arguments={})
        ])
        with self.assertRaises(SafetyError) as context:
            self.validator.validate_plan(plan)
        self.assertIn("blocked on this system", str(context.exception))

    def test_validate_plan_unregistered_tool(self):
        plan = ExecutionPlan(plan=[
            PlanItem(tool="unknown_tool", arguments={})
        ])
        needs_confirm = self.validator.validate_plan(plan)
        self.assertFalse(needs_confirm)

if __name__ == "__main__":
    unittest.main()
