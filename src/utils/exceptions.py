class VoiceAssistantError(Exception):
    """Base exception class for the Voice Assistant."""
    pass

class RecordingError(VoiceAssistantError):
    """Exception raised when audio recording fails."""
    pass

class TranscriptionError(VoiceAssistantError):
    """Exception raised when audio transcription fails."""
    pass

class TTSError(VoiceAssistantError):
    """Exception raised when Text-to-Speech generation fails."""
    pass

class AudioPlaybackError(VoiceAssistantError):
    """Exception raised when audio playback fails."""
    pass

class PlanningError(VoiceAssistantError):
    """Exception raised when LLM planning or parsing fails."""
    pass

class ExecutionError(VoiceAssistantError):
    """Exception raised when tool execution fails."""
    pass

class SafetyError(VoiceAssistantError):
    """Exception raised when execution violates safety rules."""
    pass
