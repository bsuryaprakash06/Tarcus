import time
from src.models.response import ResponseProfile, FormattedResponse
from src.response.formatter import ResponseFormatter
from src.services.metrics_service import MetricsService
from src.utils.logger import get_logger

logger = get_logger("services.response_formatter")

class ResponseFormatterService:
    """Service wrapper for formatting responses and tracking presentation metrics."""
    
    def __init__(self, metrics_service: MetricsService = None):
        self.formatter = ResponseFormatter()
        self.metrics = metrics_service or MetricsService()
        
    def format_response(self, raw_text: str, profile: ResponseProfile) -> FormattedResponse:
        """Passes text through the formatter and logs latencies."""
        start_time = time.time()
        
        try:
            formatted_response = self.formatter.format(raw_text, profile)
        except Exception as e:
            logger.error(f"Formatting failed: {e}. Falling back to raw text.")
            formatted_response = FormattedResponse(
                raw_text=raw_text,
                formatted_text=raw_text,
                ssml=f"<speak>{raw_text}</speak>",
                estimated_duration=len(raw_text.split()) / 2.5
            )
            
        latency = time.time() - start_time
        
        self.metrics.record_formatting(
            original_length=len(raw_text),
            final_length=len(formatted_response.formatted_text),
            duration=formatted_response.estimated_duration,
            latency=latency
        )
        
        return formatted_response
