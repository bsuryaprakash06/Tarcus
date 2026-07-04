import time
from src.routing.router import IntentRouter
from src.models.intent_result import RouterResult
from src.services.metrics_service import MetricsService
from src.utils.logger import get_logger

logger = get_logger("intent_router_service")

class IntentRouterService:
    """
    Service wrapper for the Intent Router to expose routing to the main loop,
    and cleanly abstract the Metric tracking logic away from the core algorithm.
    """
    def __init__(self):
        self.router = IntentRouter()
        self.metrics = MetricsService()
        
    def route_request(self, normalized_text: str) -> RouterResult:
        start_time = time.time()
        
        result = self.router.route(normalized_text)
        
        latency = time.time() - start_time
        self.metrics.record_intent(result.intent.value, latency)
        
        return result
