import hashlib
import time
from src.models.response import ResponseProfile, FormattedResponse, ResponseMode
from src.response.speech_optimizer import SpeechOptimizer
from src.utils.settings import ENABLE_SPEECH_OPTIMIZATION

class ResponseFormatter:
    """Formats text for TTS presentation, calculates durations, and caches frequent outputs."""
    
    def __init__(self):
        self._cache = {}
        
    def format(self, raw_text: str, profile: ResponseProfile) -> FormattedResponse:
        """Processes raw LLM response into a TTS-ready FormattedResponse."""
        
        # 1. Check local cache (highly effective for frequent Knowledge questions)
        cache_key = None
        if profile.mode == ResponseMode.KNOWLEDGE:
            cache_key = hashlib.md5(f"{profile.style}_{raw_text}".encode('utf-8')).hexdigest()
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        # 2. Optimize speech rhythm if enabled
        formatted_text = raw_text
        if ENABLE_SPEECH_OPTIMIZATION:
            formatted_text = SpeechOptimizer.optimize(raw_text)
            
        # 3. Prepare SSML placeholder (Future-proofing for SSML <break> tags, etc.)
        ssml = f"<speak>{formatted_text}</speak>"
        
        # 4. Estimate duration (~150 words per minute -> 2.5 words/second)
        word_count = len(formatted_text.split())
        estimated_duration = word_count / 2.5
        
        response = FormattedResponse(
            raw_text=raw_text,
            formatted_text=formatted_text,
            ssml=ssml,
            estimated_duration=estimated_duration
        )
        
        # 5. Cache the result
        if cache_key:
            self._cache[cache_key] = response
            
        return response
