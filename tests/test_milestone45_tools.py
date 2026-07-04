import pytest
import os
import time
from src.tools.take_screenshot import TakeScreenshotTool
from src.tools.close_application import CloseApplicationTool
from src.tools.open_website import OpenWebsiteTool
from src.tools.get_current_time import GetCurrentTimeTool
from src.tools.list_running_applications import ListRunningApplicationsTool
from src.tools.read_clipboard import ReadClipboardTool
from src.tools.copy_clipboard import CopyClipboardTool
from src.tools.open_file import OpenFileTool
from src.tools.rename_file import RenameFileTool
from src.tools.move_file import MoveFileTool
from src.tools.delete_file import DeleteFileTool
from src.models.plan import ExecutionContext

import src.utils.settings as settings
settings.DRY_RUN = True
os.environ["DRY_RUN"] = "True"

# Manually patch DRY_RUN for each tool module since they use 'from X import Y'
import src.tools.take_screenshot
import src.tools.close_application
import src.tools.open_website
import src.tools.list_running_applications
import src.tools.copy_clipboard
import src.tools.read_clipboard

src.tools.take_screenshot.DRY_RUN = True
src.tools.close_application.DRY_RUN = True
src.tools.open_website.DRY_RUN = True
src.tools.list_running_applications.DRY_RUN = True
src.tools.copy_clipboard.DRY_RUN = True
src.tools.read_clipboard.DRY_RUN = True

def get_dummy_context():
    return ExecutionContext(
        cwd=".",
        os="win32",
        user="test_user",
        time="2026-06-25 12:00:00",
        session_id="test",
        execution_id="test"
    )

def test_take_screenshot_dry_run():
    tool = TakeScreenshotTool()
    result = tool.execute({}, get_dummy_context())
    assert result.success == True
    assert "[DRY RUN]" in result.developer_message

def test_close_application_dry_run():
    tool = CloseApplicationTool()
    result = tool.execute({"application": "notepad"}, get_dummy_context())
    assert result.success == True
    assert "[DRY RUN]" in result.developer_message

def test_open_website_dry_run():
    tool = OpenWebsiteTool()
    result = tool.execute({"url": "google.com"}, get_dummy_context())
    assert result.success == True
    assert "[DRY RUN]" in result.developer_message

def test_get_current_time():
    tool = GetCurrentTimeTool()
    result = tool.execute({}, get_dummy_context())
    assert result.success == True
    assert "The current local date and time is" in result.developer_message

def test_list_running_applications_dry_run():
    tool = ListRunningApplicationsTool()
    result = tool.execute({}, get_dummy_context())
    assert result.success == True
    assert "[DRY RUN]" in result.developer_message

def test_copy_clipboard_dry_run():
    tool = CopyClipboardTool()
    result = tool.execute({"text": "Hello"}, get_dummy_context())
    assert result.success == True
    assert "[DRY RUN]" in result.developer_message

def test_read_clipboard_dry_run():
    tool = ReadClipboardTool()
    result = tool.execute({}, get_dummy_context())
    assert result.success == True
    assert "[DRY RUN]" in result.developer_message

def test_open_file_missing():
    tool = OpenFileTool()
    result = tool.execute({"file_path": "does_not_exist.txt"}, get_dummy_context())
    assert result.success == False
    assert "File not found" in result.developer_message

def test_rename_file_missing():
    tool = RenameFileTool()
    result = tool.execute({"source_path": "does_not_exist.txt", "new_name": "target.txt"}, get_dummy_context())
    assert result.success == False
    assert "Source file not found" in result.developer_message

def test_move_file_missing():
    tool = MoveFileTool()
    result = tool.execute({"source_path": "does_not_exist.txt", "destination_dir": "target"}, get_dummy_context())
    assert result.success == False
    assert "Source file not found" in result.developer_message

def test_delete_file_missing():
    tool = DeleteFileTool()
    result = tool.execute({"file_path": "does_not_exist.txt"}, get_dummy_context())
    assert result.success == False
    assert "File not found" in result.developer_message
