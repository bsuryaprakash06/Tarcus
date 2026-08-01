from pydantic import BaseModel

class WakeDetected(BaseModel):
    phrase: str
    confidence: float

class SpeechStarted(BaseModel):
    pass

class SpeechEnded(BaseModel):
    pass
    
class RecordingStarted(BaseModel):
    pass

class RecordingStopped(BaseModel):
    filepath: str

class TranscriptionStarted(BaseModel):
    pass

class TranscriptionCompleted(BaseModel):
    text: str
    latency: float

class PlaybackStarted(BaseModel):
    source: str

class PlaybackInterrupted(BaseModel):
    pass
    
class PlaybackCompleted(BaseModel):
    pass

class BargeInDetected(BaseModel):
    pass
