import time
from src.utils.logger import get_logger
from src.utils.settings import SILENCE_TIMEOUT_SECONDS, MIN_SPEECH_SECONDS
from src.events.pipeline_events import PipelineEventBus
from src.audio.audio_events import SpeechStarted, SpeechEnded

logger = get_logger("audio.speech_segmenter")

class SpeechSegmenter:
    """
    Monitors the SpeechDetector to determine logical utterance boundaries.
    Fires SpeechStarted and SpeechEnded events.
    """
    def __init__(self):
        self.event_bus = PipelineEventBus()
        self.in_utterance = False
        self.first_speech_time = 0.0
        self.last_speech_time = 0.0
        
    def process(self, is_speaking: bool, current_time: float = None):
        if current_time is None:
            current_time = time.time()
            
        if is_speaking:
            self.last_speech_time = current_time
            if not self.in_utterance:
                self.in_utterance = True
                self.first_speech_time = current_time
                self.event_bus.publish_event(SpeechStarted())
                logger.debug("Speech Started.")
        else:
            if self.in_utterance:
                silence_duration = current_time - self.last_speech_time
                if silence_duration >= SILENCE_TIMEOUT_SECONDS:
                    speech_duration = self.last_speech_time - self.first_speech_time
                    if speech_duration >= MIN_SPEECH_SECONDS:
                        logger.debug(f"Speech Ended (Duration: {speech_duration:.2f}s)")
                        self.event_bus.publish_event(SpeechEnded())
                    else:
                        logger.debug("Speech Ended (Too short, discarded)")
                        
                    self.in_utterance = False
                    self.first_speech_time = 0.0
                    
    def reset(self):
        self.in_utterance = False
        self.first_speech_time = 0.0
        self.last_speech_time = 0.0
