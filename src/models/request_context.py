import uuid
from src.services.diagnostics_service import DiagnosticsService
from src.services.metrics_service import MetricsService
from src.services.history_service import CommandHistoryService

class RequestContext:
    """
    Holds the execution context and decoupled telemetry tools for a single interaction.
    Prevents Singleton crosstalk when processing multiple commands or background tasks.
    """
    def __init__(self, request_id: str = None):
        self.request_id = request_id or str(uuid.uuid4())
        self.diagnostics = DiagnosticsService()
        
        # We inject the current Singletons here so that future iterations can swap
        # them out with request-scoped history/metrics if needed.
        self.metrics = MetricsService()
        self.history = CommandHistoryService()
