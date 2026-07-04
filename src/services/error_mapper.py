from dataclasses import dataclass
from src.models.error_codes import ErrorCode

@dataclass
class MappedError:
    error_code: ErrorCode
    user_message: str

class ErrorMapper:
    """
    Service to map internal Python exceptions to user-friendly spoken phrases and strict error codes.
    Prevents leaking absolute paths or stack traces into the Text-to-Speech engine.
    """
    
    @staticmethod
    def to_user_message(error: Exception) -> MappedError:
        if isinstance(error, FileNotFoundError):
            return MappedError(ErrorCode.FILE_NOT_FOUND, "I couldn't find the requested file.")
        elif isinstance(error, PermissionError):
            return MappedError(ErrorCode.PERMISSION_DENIED, "I don't have permission to perform that action.")
        elif isinstance(error, TimeoutError):
            return MappedError(ErrorCode.TIMEOUT, "That operation took too long.")
        elif isinstance(error, ConnectionError):
            return MappedError(ErrorCode.CONNECTION_ERROR, "I couldn't connect to the required service.")
        
        # Generic fallback for unknown execution errors
        return MappedError(ErrorCode.UNKNOWN, "Something went wrong while completing your request.")
