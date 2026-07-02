import datetime
from pydantic import BaseModel, Field
from src.models.plan import ExecutionPlan, ToolResult
from src.utils.logger import get_logger

logger = get_logger("history")

class HistoryRecord(BaseModel):
    """
    Represents a full record of a single request's lifecycle.
    """
    execution_id: str
    timestamp: str
    voice_command: str
    transcription: str
    plan: ExecutionPlan | None = None
    tool_results: list[ToolResult] | None = None
    planner_latency: float = 0.0
    execution_duration: float = 0.0
    overall_status: str = "PENDING"

class CommandHistoryService:
    """
    Singleton service that tracks the execution history in memory.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandHistoryService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        self.history: list[HistoryRecord] = []
        
    def create_record(self, execution_id: str, voice_command: str = "") -> HistoryRecord:
        """Initializes a new history record."""
        record = HistoryRecord(
            execution_id=execution_id,
            timestamp=datetime.datetime.now().isoformat(),
            voice_command=voice_command,
            transcription=""
        )
        self.history.append(record)
        return record
        
    def get_record(self, execution_id: str) -> HistoryRecord | None:
        """Retrieves a record by execution_id."""
        for record in self.history:
            if record.execution_id == execution_id:
                return record
        return None
