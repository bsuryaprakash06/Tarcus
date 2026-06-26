import unittest
from src.brain.prompt_builder import PromptBuilder
from src.tools.registry import ToolRegistry

class TestPromptBuilder(unittest.TestCase):
    def test_build_prompt(self):
        registry = ToolRegistry()
        builder = PromptBuilder(registry)
        prompt = builder.build_prompt()
        
        self.assertIn("open_application", prompt)
        self.assertIn("create_folder", prompt)
        self.assertIn("search_web", prompt)
        self.assertIn("Safety Level:", prompt)
        self.assertIn("Category:", prompt)
        self.assertIn("Examples:", prompt)
