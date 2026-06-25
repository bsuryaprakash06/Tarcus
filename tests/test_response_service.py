import unittest
from src.services.response_service import ResponseService, ResponseMode

class TestResponseService(unittest.TestCase):
    def setUp(self):
        self.service = ResponseService()
        
    def test_formulate_response_success(self):
        res = self.service.formulate_response("Open Notepad", ResponseMode.SUCCESS)
        self.assertEqual(res, "I heard: Open Notepad")
        
    def test_formulate_response_empty_success(self):
        res = self.service.formulate_response("", ResponseMode.SUCCESS)
        self.assertEqual(res, "I didn't catch that. Could you please repeat it?")
        
    def test_formulate_response_error(self):
        res = self.service.formulate_response("file not found", ResponseMode.ERROR)
        self.assertEqual(res, "An error occurred: file not found")
        
        res_default = self.service.formulate_response("", ResponseMode.ERROR)
        self.assertEqual(res_default, "Something went wrong. Please try again.")

    def test_formulate_response_warning(self):
        res = self.service.formulate_response("low battery", ResponseMode.WARNING)
        self.assertEqual(res, "Warning: low battery")

    def test_formulate_response_info(self):
        res = self.service.formulate_response("Connecting...", ResponseMode.INFO)
        self.assertEqual(res, "Connecting...")
