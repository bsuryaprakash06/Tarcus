from src.models.plan import ToolResult
from src.models.response import ResponseMode

class ResponseService:
    """Service layer class to formulate conversational agent responses."""
    
    def formulate_response(self, text: str, mode: ResponseMode = ResponseMode.CONFIRMATION) -> str:
        """
        Formulates a voice response based on the text and conversation mode.
        """
        clean_text = text.strip()
        
        if mode == ResponseMode.ERROR:
            return f"An error occurred: {clean_text}" if clean_text else "Something went wrong. Please try again."
        elif mode == ResponseMode.WARNING:
            return f"Warning: {clean_text}"
        elif mode == ResponseMode.CONVERSATION:
            return clean_text
            
        # Default: CONFIRMATION / conversational response
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
                success_messages.append(res.user_message)
            else:
                failure_messages.append(res.user_message)
                
        def _aggregate_messages(messages: list[str]) -> str:
            if not messages:
                return ""
                
            # Basic grouping by the first word (verb) to reduce repetition
            from collections import defaultdict
            groups = defaultdict(list)
            
            for msg in messages:
                msg = msg.strip().rstrip('.')
                parts = msg.split(' ', 1)
                if len(parts) == 2:
                    groups[parts[0]].append(parts[1])
                else:
                    groups[msg].append("")
                    
            combined = []
            for prefix, suffixes in groups.items():
                # If there's no suffix (e.g., one word message)
                if len(suffixes) == 1 and not suffixes[0]:
                    combined.append(prefix)
                elif len(suffixes) == 1:
                    combined.append(f"{prefix} {suffixes[0]}")
                else:
                    last = suffixes.pop()
                    if len(suffixes) > 1:
                        combined.append(f"{prefix} {', '.join(suffixes)}, and {last}")
                    else:
                        combined.append(f"{prefix} {suffixes[0]} and {last}")
                        
            return ". ".join(combined) + "."
                
        if failure_messages and not success_messages:
            return f"I encountered some issues: {_aggregate_messages(failure_messages)}"
        elif failure_messages and success_messages:
            return f"I partially completed the plan. {_aggregate_messages(success_messages)} However, {_aggregate_messages(failure_messages)}"
            
        return _aggregate_messages(success_messages)
