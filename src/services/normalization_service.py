from src.normalization.speech_normalizer import SpeechNormalizer
from src.models.normalization import NormalizationResult
from src.services.metrics_service import MetricsService
from src.utils.logger import get_logger

logger = get_logger("normalization_service")

class NormalizationService:
    """
    Service wrapper for the deterministic Speech Normalizer.
    Responsible for bridging the normalizer with the MetricsService.
    """
    def __init__(self):
        self.normalizer = SpeechNormalizer()
        self.metrics = MetricsService()
        
    def normalize_transcription(self, text: str) -> NormalizationResult:
        result = self.normalizer.normalize(text)
        
        # Track metrics
        was_normalized = len(result.changes) > 0
        changed_terms = [change.normalized for change in result.changes]
        
        self.metrics.record_normalization(was_normalized, changed_terms)
        
        return result
