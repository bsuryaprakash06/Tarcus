from enum import Enum

class ResponseMode(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class ResponseService:
    """Service layer class to formulate conversational agent responses."""
    
    def formulate_response(self, text: str, mode: ResponseMode = ResponseMode.SUCCESS) -> str:
        """
        Formulates a voice response based on the text and conversation mode.
        """
        clean_text = text.strip()
        
        if mode == ResponseMode.ERROR:
            return f"An error occurred: {clean_text}" if clean_text else "Something went wrong. Please try again."
        elif mode == ResponseMode.WARNING:
            return f"Warning: {clean_text}"
        elif mode == ResponseMode.INFO:
            return clean_text
            
        # Default: SUCCESS / conversational response
        if not clean_text:
            return "I didn't catch that. Could you please repeat it?"
            
        # If user spoke successfully, echo the text
        return f"I heard: {clean_text}"
