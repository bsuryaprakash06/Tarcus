import unittest
from unittest.mock import patch, MagicMock
import requests
from src.services.llm_service import LLMService
from src.utils.exceptions import PlanningError
from src.models.plan import ExecutionPlan, PlanItem

class TestLLMService(unittest.TestCase):
    def setUp(self):
        self.service = LLMService()

    @patch("requests.post")
    def test_generate_plan_success_first_try(self, mock_post):
        # Mock successful JSON response matching the plan schema
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": '{"plan": [{"tool": "open_application", "arguments": {"application": "notepad"}}]}'
            }
        }
        mock_post.return_value = mock_response

        plan = self.service.generate_plan("Open Notepad")
        
        # Verify result is structured correctly
        self.assertIsInstance(plan, ExecutionPlan)
        self.assertEqual(len(plan.plan), 1)
        self.assertEqual(plan.plan[0].tool, "open_application")
        self.assertEqual(plan.plan[0].arguments, {"application": "notepad"})
        
        # Verify correct payload options were sent
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        payload = kwargs["json"]
        self.assertEqual(payload["options"]["thinking"], False)
        self.assertEqual(payload["think"], False)
        self.assertEqual(payload["options"]["temperature"], 0.0)

    @patch("requests.post")
    def test_generate_plan_markdown_stripping(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": '```json\n{"plan": [{"tool": "search_web", "arguments": {"query": "weather"}}]}\n```'
            }
        }
        mock_post.return_value = mock_response

        plan = self.service.generate_plan("search weather")
        self.assertEqual(plan.plan[0].tool, "search_web")
        self.assertEqual(plan.plan[0].arguments, {"query": "weather"})

    @patch("requests.post")
    def test_generate_plan_retry_success(self, mock_post):
        # First request returns invalid JSON, second request succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 200
        mock_response_fail.json.return_value = {
            "message": {
                "content": 'invalid json here'
            }
        }
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            "message": {
                "content": '{"plan": [{"tool": "create_folder", "arguments": {"name": "test"}}]}'
            }
        }
        
        mock_post.side_effect = [mock_response_fail, mock_response_success]

        plan = self.service.generate_plan("make a folder test")
        self.assertEqual(plan.plan[0].tool, "create_folder")
        self.assertEqual(mock_post.call_count, 2)

    @patch("requests.post")
    def test_generate_plan_max_retries_exceeded(self, mock_post):
        # All requests return invalid JSON
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 200
        mock_response_fail.json.return_value = {
            "message": {
                "content": 'corrupt json'
            }
        }
        mock_post.return_value = mock_response_fail

        with self.assertRaises(PlanningError):
            self.service.generate_plan("open calc")
            
        self.assertEqual(mock_post.call_count, 3)

    @patch("requests.post")
    def test_generate_plan_http_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with self.assertRaises(PlanningError):
            self.service.generate_plan("open calc")

if __name__ == "__main__":
    unittest.main()
