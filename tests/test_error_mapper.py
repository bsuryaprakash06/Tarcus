import unittest
from src.services.error_mapper import ErrorMapper
from src.models.error_codes import ErrorCode

class TestErrorMapper(unittest.TestCase):

    def test_file_not_found_error(self):
        err = FileNotFoundError("C:\\Users\\Shane\\Desktop\\secret_file.txt")
        mapped = ErrorMapper.to_user_message(err)
        
        self.assertEqual(mapped.error_code, ErrorCode.FILE_NOT_FOUND)
        self.assertEqual(mapped.user_message, "I couldn't find the requested file.")
        
        # Regression Test: Ensure absolute path did NOT leak into the user message
        self.assertNotIn("C:\\", mapped.user_message)
        self.assertNotIn("secret_file.txt", mapped.user_message)
        self.assertNotIn("FileNotFoundError", mapped.user_message)

    def test_permission_error(self):
        err = PermissionError("Access is denied to C:\\Windows\\System32")
        mapped = ErrorMapper.to_user_message(err)
        
        self.assertEqual(mapped.error_code, ErrorCode.PERMISSION_DENIED)
        self.assertEqual(mapped.user_message, "I don't have permission to perform that action.")
        
        self.assertNotIn("C:\\", mapped.user_message)

    def test_timeout_error(self):
        err = TimeoutError("Network request timed out.")
        mapped = ErrorMapper.to_user_message(err)
        
        self.assertEqual(mapped.error_code, ErrorCode.TIMEOUT)

    def test_unknown_error(self):
        err = ValueError("Something completely unexpected happened")
        mapped = ErrorMapper.to_user_message(err)
        
        self.assertEqual(mapped.error_code, ErrorCode.UNKNOWN)
        self.assertEqual(mapped.user_message, "Something went wrong while completing your request.")
        self.assertNotIn("ValueError", mapped.user_message)

if __name__ == "__main__":
    unittest.main()
