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
