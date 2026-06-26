import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import os

from src.tools.open_application import OpenApplicationTool
from src.tools.create_folder import CreateFolderTool
from src.tools.search_web import SearchWebTool
from src.models.plan import ExecutionContext
from src.tools.base_tool import SafetyLevel

class TestTools(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # Create a mock 'cwd' which has a parent to test location resolution
        self.mock_cwd = os.path.join(self.temp_dir, "Voice-Assistant")
        os.makedirs(self.mock_cwd, exist_ok=True)
        
        self.context = ExecutionContext(
            cwd=self.mock_cwd,
            os="win32",
            user="test_user",
            time="2026-06-25 12:00:00",
            clipboard=""
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @patch("subprocess.Popen")
    def test_open_application_success(self, mock_popen):
        tool = OpenApplicationTool()
        self.assertEqual(tool.name, "open_application")
        self.assertEqual(tool.category, "System")
        self.assertEqual(tool.safety_level, SafetyLevel.SAFE)
        
        result = tool.execute({"application": "calc"}, self.context)
        self.assertTrue(result.success)
        self.assertIn("calc", result.message)
        mock_popen.assert_called_once_with("start calc", shell=True)

    def test_open_application_invalid_name(self):
        tool = OpenApplicationTool()
        result = tool.execute({"application": "calc; ls"}, self.context)
        self.assertFalse(result.success)
        self.assertIn("Invalid application name format", result.message)

    def test_open_application_missing_name(self):
        tool = OpenApplicationTool()
        result = tool.execute({}, self.context)
        self.assertFalse(result.success)
        self.assertIn("missing or empty", result.message)

    def test_create_folder_root(self):
        tool = CreateFolderTool()
        self.assertEqual(tool.name, "create_folder")
        self.assertEqual(tool.category, "Files")
        
        result = tool.execute({"name": "physics", "location": "root"}, self.context)
        self.assertTrue(result.success)
        
        expected_path = Path(self.mock_cwd) / "physics"
        self.assertTrue(expected_path.exists())
        self.assertEqual(result.data["path"], str(expected_path))

    def test_create_folder_documents(self):
        tool = CreateFolderTool()
        result = tool.execute({"name": "physics", "location": "documents"}, self.context)
        self.assertTrue(result.success)
        
        expected_path = Path(self.mock_cwd).parent / "physics"
        self.assertTrue(expected_path.exists())
        self.assertEqual(result.data["path"], str(expected_path))

    def test_create_folder_traversal_guard(self):
        tool = CreateFolderTool()
        # Try to traverse out of the base folder
        result = tool.execute({"name": "../traversal_dir", "location": "root"}, self.context)
        self.assertFalse(result.success)
        self.assertIn("traversal attempt detected", result.message)

    def test_create_folder_missing_name(self):
        tool = CreateFolderTool()
        result = tool.execute({}, self.context)
        self.assertFalse(result.success)
        self.assertIn("missing or empty", result.message)

    @patch("webbrowser.open")
    def test_search_web_success(self, mock_web_open):
        tool = SearchWebTool()
        self.assertEqual(tool.name, "search_web")
        self.assertEqual(tool.category, "Browser")
        
        result = tool.execute({"query": "python programming"}, self.context)
        self.assertTrue(result.success)
        mock_web_open.assert_called_once_with("https://www.google.com/search?q=python programming")

    def test_search_web_missing_query(self):
        tool = SearchWebTool()
        result = tool.execute({}, self.context)
        self.assertFalse(result.success)
        self.assertIn("missing or empty", result.message)

if __name__ == "__main__":
    unittest.main()
