import unittest
from unittest.mock import patch, MagicMock
import requests
import time

from src.services.llm_service import LLMService
from src.brain.planner import Planner
from src.brain.parser import parse_execution_plan, validate_plan_semantics
from src.models.plan import ExecutionPlan, PlanItem
from src.providers import BaseProvider, ProviderResponse, get_provider_from_settings
from src.providers.ollama_provider import OllamaProvider
from src.providers.openai_provider import OpenAIProvider
from src.providers.groq_provider import GroqProvider
from src.tools.registry import ToolRegistry
from src.tools.base_tool import BaseTool, SafetyLevel
from src.utils.exceptions import PlanningError

class MockProvider(BaseProvider):
    """Mock implementation of BaseProvider for testing Planner retry loops."""
    
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_count = 0
        self.last_user_prompts = []

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def supports_json_mode(self) -> bool:
        return True

    @property
    def supports_streaming(self) -> bool:
        return False

    @property
    def supports_vision(self) -> bool:
        return False

    @property
    def supports_tool_calling(self) -> bool:
        return False

    def generate(self, system_prompt: str, user_prompt: str) -> ProviderResponse:
        self.call_count += 1
        self.last_user_prompts.append(user_prompt)
        text = self.responses[self.call_count - 1]
        return ProviderResponse(
            text=text,
            model_name="mock-model",
            provider_name=self.provider_name,
            latency=0.01,
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        )

class TestLLMService(unittest.TestCase):
    
    # ----------------------------------------------------
    # Provider Payload Tests
    # ----------------------------------------------------

    @patch("requests.post")
    def test_ollama_provider_payload(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "ollama_response"},
            "prompt_eval_count": 50,
            "eval_count": 25
        }
        mock_post.return_value = mock_response

        # Temporarily patch settings for Ollama
        with patch("src.providers.ollama_provider.MODEL_NAME", "qwen3:4b"), \
             patch("src.providers.ollama_provider.BASE_URL", "http://localhost:11434"):
            provider = OllamaProvider()
            self.assertEqual(provider.provider_name, "ollama")
            self.assertFalse(provider.supports_json_mode)
            self.assertTrue(provider.supports_streaming)
            
            res = provider.generate("sys_prompt", "user_prompt")
            
            self.assertEqual(res.text, "ollama_response")
            self.assertEqual(res.provider_name, "ollama")
            self.assertEqual(res.usage["total_tokens"], 75)
            
            # Assert payload options
            mock_post.assert_called_once()
            _, kwargs = mock_post.call_args
            payload = kwargs["json"]
            self.assertEqual(payload["model"], "qwen3:4b")
            self.assertEqual(payload["think"], False)
            self.assertEqual(payload["options"]["thinking"], False)
            self.assertEqual(payload["options"]["temperature"], 0.0)

    @patch("requests.post")
    def test_openai_provider_payload(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "openai_response"}}],
            "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30}
        }
        mock_post.return_value = mock_response

        with patch("src.providers.openai_provider.MODEL_NAME", "gpt-4o"), \
             patch("src.providers.openai_provider.OPENAI_API_KEY", "sk-test-key"), \
             patch("src.providers.openai_provider.BASE_URL", "https://api.openai.com/v1/chat/completions"):
            provider = OpenAIProvider()
            self.assertEqual(provider.provider_name, "openai")
            self.assertTrue(provider.supports_json_mode)
            
            res = provider.generate("sys_prompt", "user_prompt")
            
            self.assertEqual(res.text, "openai_response")
            self.assertEqual(res.provider_name, "openai")
            self.assertEqual(res.usage["total_tokens"], 30)
            
            mock_post.assert_called_once()
            _, kwargs = mock_post.call_args
            payload = kwargs["json"]
            headers = kwargs["headers"]
            self.assertEqual(payload["model"], "gpt-4o")
            self.assertEqual(payload["response_format"], {"type": "json_object"})
            self.assertEqual(headers["Authorization"], "Bearer sk-test-key")

    @patch("requests.post")
    def test_groq_provider_payload(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "groq_response"}}],
            "usage": {"prompt_tokens": 15, "completion_tokens": 8, "total_tokens": 23}
        }
        mock_post.return_value = mock_response

        with patch("src.providers.groq_provider.MODEL_NAME", "llama-3.3-70b-versatile"), \
             patch("src.providers.groq_provider.GROQ_API_KEY", "gsk-test-key"), \
             patch("src.providers.groq_provider.BASE_URL", "https://api.groq.com/openai/v1/chat/completions"):
            provider = GroqProvider()
            self.assertEqual(provider.provider_name, "groq")
            self.assertTrue(provider.supports_json_mode)
            self.assertTrue(provider.supports_tool_calling)
            
            res = provider.generate("sys_prompt", "user_prompt")
            
            self.assertEqual(res.text, "groq_response")
            self.assertEqual(res.usage["total_tokens"], 23)
            
            mock_post.assert_called_once()
            _, kwargs = mock_post.call_args
            payload = kwargs["json"]
            headers = kwargs["headers"]
            self.assertEqual(payload["model"], "llama-3.3-70b-versatile")
            self.assertEqual(payload["response_format"], {"type": "json_object"})
            self.assertEqual(headers["Authorization"], "Bearer gsk-test-key")

    # ----------------------------------------------------
    # Planner Smart Retry Logic Tests
    # ----------------------------------------------------

    def test_planner_smart_retry_success(self):
        # Attempt 1: Returns corrupt JSON
        # Attempt 2: Returns valid JSON plan
        responses = [
            "corrupt json block",
            '{"plan": [{"tool": "open_application", "arguments": {"application": "calc"}}]}'
        ]
        mock_provider = MockProvider(responses)
        registry = ToolRegistry()
        planner = Planner(provider=mock_provider, tool_registry=registry)
        
        plan = planner.plan("Open Calculator")
        
        self.assertEqual(mock_provider.call_count, 2)
        self.assertEqual(len(plan.plan), 1)
        self.assertEqual(plan.plan[0].tool, "open_application")
        
        # Verify the second user prompt contains the validation error message (smart retry)
        self.assertEqual(mock_provider.last_user_prompts[0], "Open Calculator")
        self.assertIn("LLM did not return valid JSON", mock_provider.last_user_prompts[1])
        self.assertIn("Open Calculator", mock_provider.last_user_prompts[1])

    def test_planner_max_retries_failure(self):
        responses = ["corrupt json", "corrupt json", "corrupt json"]
        mock_provider = MockProvider(responses)
        planner = Planner(provider=mock_provider)
        
        with self.assertRaises(PlanningError):
            planner.plan("Open Calculator")
            
        self.assertEqual(mock_provider.call_count, 3)

    # ----------------------------------------------------
    # Stage 3 Semantic Validation Tests
    # ----------------------------------------------------

    def test_semantic_validation_tool_not_exists(self):
        registry = ToolRegistry()
        plan = ExecutionPlan(plan=[
            PlanItem(tool="non_existent_tool", arguments={})
        ])
        with self.assertRaises(PlanningError) as context:
            validate_plan_semantics(plan, registry)
        self.assertIn("is not registered", str(context.exception))

    def test_semantic_validation_unknown_argument(self):
        registry = ToolRegistry()
        plan = ExecutionPlan(plan=[
            PlanItem(tool="open_application", arguments={"app": "calc", "unknown_arg": "test"})
        ])
        with self.assertRaises(PlanningError) as context:
            validate_plan_semantics(plan, registry)
        self.assertIn("does not accept argument 'app'", str(context.exception))

    def test_semantic_validation_missing_required_argument(self):
        registry = ToolRegistry()
        plan = ExecutionPlan(plan=[
            PlanItem(tool="open_application", arguments={})
        ])
        with self.assertRaises(PlanningError) as context:
            validate_plan_semantics(plan, registry)
        self.assertIn("requires argument 'application' which is missing", str(context.exception))

    def test_semantic_validation_empty_required_string(self):
        registry = ToolRegistry()
        plan = ExecutionPlan(plan=[
            PlanItem(tool="open_application", arguments={"application": "   "})
        ])
        with self.assertRaises(PlanningError) as context:
            validate_plan_semantics(plan, registry)
        self.assertIn("cannot be empty or whitespace-only", str(context.exception))

    def test_semantic_validation_type_mismatch(self):
        registry = ToolRegistry()
        plan = ExecutionPlan(plan=[
            PlanItem(tool="open_application", arguments={"application": 12345})
        ])
        with self.assertRaises(PlanningError) as context:
            validate_plan_semantics(plan, registry)
        self.assertIn("must be a string", str(context.exception))

    def test_semantic_validation_invalid_enum_value(self):
        registry = ToolRegistry()
        # CreateFolderTool accepts enum choices ["documents", "root"]
        plan = ExecutionPlan(plan=[
            PlanItem(tool="create_folder", arguments={"name": "test", "location": "invalid_loc"})
        ])
        with self.assertRaises(PlanningError) as context:
            validate_plan_semantics(plan, registry)
        self.assertIn("value 'invalid_loc' is not valid. Allowed values", str(context.exception))

if __name__ == "__main__":
    unittest.main()
