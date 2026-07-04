from pydantic import BaseModel, Field

class TranscriptionResult(BaseModel):
    """Data model representing the structured result of an audio transcription."""
    text: str = Field(description="The transcribed text output.")
    language: str = Field(description="The detected language code (e.g., 'en').")
    duration: float = Field(description="The duration of the audio in seconds.")
