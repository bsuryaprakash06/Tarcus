from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .audio_state import AudioState
import time

class AudioSession(BaseModel):
    """
    The Single Source of Truth for the Audio Subsystem Dashboard.
    """
    # State
    state: AudioState = AudioState.IDLE
    microphone_active: bool = False
    tts_active: bool = False
    recording_active: bool = False
    interrupted: bool = False
    
    # Levels & Confidence
    mic_level: float = 0.0
    playback_level: float = 0.0
    wake_confidence: float = 0.0
    speech_confidence: float = 0.0
    
    # Active Streams & Devices
    input_device: Optional[str] = None
    output_device: Optional[str] = None
    current_stream_id: Optional[str] = None
    current_provider: Optional[str] = None
    current_speaker: str = "user" # 'user' or 'assistant'
    
    # Metrics
    latencies: Dict[str, float] = Field(default_factory=dict)
    
    def touch_latency(self, metric_name: str, start_time: float):
        self.latencies[metric_name] = time.time() - start_time
