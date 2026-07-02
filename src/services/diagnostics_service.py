import time
from src.utils.logger import get_logger
from src.utils.settings import ENABLE_DIAGNOSTICS

logger = get_logger("diagnostics")

class DiagnosticsService:
    """
    Tracks and reports execution timings for each stage of the assistant's pipeline.
    """
    def __init__(self):
        self.timings = {
            "Speech Recognition": 0.0,
            "Planner": 0.0,
            "Validation": 0.0,
            "Execution": 0.0,
            "TTS": 0.0,
            "Playback": 0.0
        }
        self._start_times = {}
        self.request_start_time = time.time()

    def start_timer(self, stage: str) -> None:
        """Starts the timer for a specific pipeline stage."""
        self._start_times[stage] = time.time()

    def stop_timer(self, stage: str) -> None:
        """Stops the timer and records the duration."""
        if stage in self._start_times:
            duration = time.time() - self._start_times[stage]
            self.timings[stage] = duration
            del self._start_times[stage]

    def set_duration(self, stage: str, duration: float) -> None:
        """Manually sets the duration for a stage."""
        self.timings[stage] = duration

    def print_summary(self) -> None:
        """Prints the formatted diagnostic summary if enabled."""
        if not ENABLE_DIAGNOSTICS:
            return
            
        total_time = time.time() - self.request_start_time
        
        summary = [
            "",
            "Performance Summary",
            "-" * 20
        ]
        
        for stage, duration in self.timings.items():
            if duration > 0:
                summary.append(f"{stage:25} {duration:.2f} s")
                
        summary.append("-" * 20)
        summary.append(f"{'Total':25} {total_time:.2f} s")
        summary.append("")
        
        # Print directly to console for visibility, and log at debug level
        summary_text = "\n".join(summary)
        print(summary_text)
        logger.debug(f"Diagnostics:\n{summary_text}")
