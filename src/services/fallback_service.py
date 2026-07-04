class FallbackService:
    """
    Gracefully handles routing failures, low confidence predictions, mixed intents, 
    and unknown requests without exposing technical errors to the user.
    """
    def handle_low_confidence(self) -> str:
        return "I wasn't quite sure what you meant. Could you rephrase your request?"
        
    def handle_mixed_intent(self) -> str:
        return "It sounds like you're asking me to do multiple different things. Please ask me one thing at a time."
        
    def handle_unknown(self) -> str:
        return "I'm sorry, I don't know how to handle that type of request yet."
