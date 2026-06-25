class VoiceAssistantError(Exception):
    """Base exception class for the Voice Assistant."""
    pass

class RecordingError(VoiceAssistantError):
    """Exception raised when audio recording fails."""
    pass

class TranscriptionError(VoiceAssistantError):
    """Exception raised when audio transcription fails."""
    pass
