from enum import Enum
from src.models.plan import ToolResult

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

    def formulate_execution_response(self, results: list[ToolResult]) -> str:
        """
        Formulates a natural language summary of the tool execution results.
        """
        if not results:
            return "I didn't find any actions to perform."
            
        success_messages = []
        failure_messages = []
        
        for res in results:
            if res.success:
                success_messages.append(res.message)
            else:
                failure_messages.append(res.message)
                
        if failure_messages and not success_messages:
            return f"I encountered some issues: {'; '.join(failure_messages)}"
        elif failure_messages and success_messages:
            return f"I partially completed the plan: {'; '.join(success_messages)}. However, {'; '.join(failure_messages)}"
            
        return " and ".join(success_messages)
