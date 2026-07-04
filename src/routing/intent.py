from enum import Enum

class Intent(str, Enum):
    """
    Categorizes the primary intent of a user's spoken command.
    Used by the IntentRouter to dispatch to the correct service.
    """
    AUTOMATION = "AUTOMATION"       # System commands, UI actions, file manipulations
    LLM_CHAT = "LLM_CHAT"           # General questions, explanations, text generation
    CONVERSATION = "CONVERSATION"   # Greetings, pleasantries, small talk
    MIXED = "MIXED"                 # Multi-part requests spanning multiple intents
    UNKNOWN = "UNKNOWN"             # Unrecognizable or nonsensical input
    
    # --- Future Architecture Slots ---
    BROWSER = "BROWSER"             # Complex web automation / scraping
    VISION = "VISION"               # Screen understanding, visual questions
    WORKFLOW = "WORKFLOW"           # Multi-step chained workflows
    MEMORY = "MEMORY"               # Remembering facts, recalling context
