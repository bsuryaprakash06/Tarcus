import unittest
from unittest.mock import patch, MagicMock
from src.services.executor_service import ExecutorService
from src.models.plan import ExecutionPlan, PlanItem, ExecutionContext, ToolResult
from src.tools.registry import ToolRegistry
from src.tools.base_tool import BaseTool, SafetyLevel

class MockTool(BaseTool):
    @property
    def name(self) -> str:
        return "mock_tool"
        
    @property
    def description(self) -> str:
        return "A mock tool for testing."
        
    @property
    def arguments_schema(self) -> dict:
        return {"param": {"type": "string"}}
        
    @property
    def examples(self) -> list[str]:
        return ["Run mock tool"]
        
    @property
    def category(self) -> str:
        return "Test"

    def execute(self, arguments: dict, context: ExecutionContext) -> ToolResult:
        param = arguments.get("param", "")
        if param == "fail":
            return ToolResult(tool_name=self.name, success=False, message="Simulated tool failure.", duration=0.05)
        elif param == "error":
            raise ValueError("Unexpected tool crash")
        return ToolResult(tool_name=self.name, success=True, message=f"Executed with {param}", duration=0.1, data={"echo": param})

class TestExecutorService(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()
        self.mock_tool = MockTool()
        self.registry.register(self.mock_tool)
        self.executor = ExecutorService(tool_registry=self.registry)

    @patch("os.getlogin")
    def test_get_current_context(self, mock_login):
        mock_login.return_value = "john_doe"
        
        context = self.executor.get_current_context()
        
        self.assertIsInstance(context, ExecutionContext)
        self.assertEqual(context.user, "john_doe")
        self.assertIsNotNone(context.cwd)
        self.assertIsNotNone(context.os)
        self.assertIsNotNone(context.time)
        self.assertIsNotNone(context.session_id)
        self.assertIsNotNone(context.execution_id)

    @patch("os.getlogin")
    def test_execute_plan_success(self, mock_login):
        mock_login.return_value = "john_doe"
        
        plan = ExecutionPlan(plan=[
            PlanItem(tool="mock_tool", arguments={"param": "hello"}),
            PlanItem(tool="mock_tool", arguments={"param": "world"})
        ])
        
        results = self.executor.execute_plan(plan)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].message, "Executed with hello")
        self.assertEqual(results[0].data, {"echo": "hello"})
        self.assertGreater(results[0].duration, 0)
        
        self.assertTrue(results[1].success)
        self.assertEqual(results[1].message, "Executed with world")

    @patch("os.getlogin")
    def test_execute_plan_tool_not_found(self, mock_login):
        mock_login.return_value = "john_doe"
        
        plan = ExecutionPlan(plan=[
            PlanItem(tool="unknown_tool", arguments={})
        ])
        
        results = self.executor.execute_plan(plan)
        
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertIn("is not supported", results[0].message)

    @patch("os.getlogin")
    def test_execute_plan_tool_failure(self, mock_login):
        mock_login.return_value = "john_doe"
        
        plan = ExecutionPlan(plan=[
            PlanItem(tool="mock_tool", arguments={"param": "fail"})
        ])
        
        results = self.executor.execute_plan(plan)
        
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertEqual(results[0].message, "Simulated tool failure.")

    @patch("os.getlogin")
    def test_execute_plan_tool_exception(self, mock_login):
        mock_login.return_value = "john_doe"
        
        plan = ExecutionPlan(plan=[
            PlanItem(tool="mock_tool", arguments={"param": "error"})
        ])
        
        results = self.executor.execute_plan(plan)
        
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertIn("Unexpected tool crash", results[0].message)

if __name__ == "__main__":
    unittest.main()
