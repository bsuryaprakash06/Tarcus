class ShortTermMemory:
    """
    Manages session-level conversational history and context for the assistant.
    Provides storage and retrieval of recent user commands, generated plans,
    and system responses.
    """
    
    def __init__(self):
        self.history = []

    def add_message(self, role: str, content: str) -> None:
        """Adds a message to the active session history."""
        self.history.append({"role": role, "content": content})

    def get_history(self) -> list[dict]:
        """Returns the complete list of session history messages."""
        return self.history

    def clear(self) -> None:
        """Clears the session history."""
        self.history.clear()
