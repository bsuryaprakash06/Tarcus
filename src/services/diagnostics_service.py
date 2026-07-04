import time
from src.utils.logger import get_logger
from src.utils.settings import ENABLE_DIAGNOSTICS

logger = get_logger("diagnostics")

class DiagnosticsService:
    """
    Tracks and reports execution timings for each stage of the assistant's pipeline.
    Instantiated per-request via RequestContext.
    """
    def __init__(self):
        self.timings = {
            "Speech Duration": 0.0,
            "Silence Detection": 0.0,
            "Whisper": 0.0,
            "Planner": 0.0,
            "Execution": 0.0,
            "TTS": 0.0,
            "Playback": 0.0,
            "Response Latency": 0.0
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

    def calculate_metrics(self) -> None:
        """Calculate derived metrics like Response Latency."""
        # User Wait Time starts from end of speech until TTS playback (or TTS generation) starts
        # A simple approximation: Whisper + Planner + Execution + Silence Detection
        latency = self.timings.get("Whisper", 0.0) + self.timings.get("Planner", 0.0) + self.timings.get("Execution", 0.0)
        latency += self.timings.get("Silence Detection", 0.0)
        self.timings["Response Latency"] = latency

    def print_summary(self) -> None:
        """Prints the formatted diagnostic summary if enabled, including performance warnings."""
        if not ENABLE_DIAGNOSTICS:
            return
            
        self.calculate_metrics()
        total_time = time.time() - self.request_start_time
        
        summary = [
            "",
            "Performance Summary",
            "-" * 40
        ]
        
        warnings = []
        score_penalty = 0.0
        
        for stage, duration in self.timings.items():
            if duration > 0:
                status = "PASS"
                if stage == "Planner" and duration > 1.0:
                    status = "WARNING"
                    warnings.append("⚠ Planner latency is above target.")
                    score_penalty += 1.0
                elif stage == "TTS" and duration > 1.0:
                    status = "WARNING"
                    warnings.append("⚠ Speech generation is slower than expected.")
                    score_penalty += 1.0
                elif stage == "Whisper" and duration > 1.5:
                    status = "WARNING"
                    warnings.append("⚠ Transcription is slower than expected.")
                    score_penalty += 0.5
                    
                summary.append(f"{stage:20} {duration:5.2f} s  [{status}]")
                
        # Overall Score out of 10
        base_score = 10.0 - score_penalty
        score = max(0.0, round(base_score, 1))

        summary.append("-" * 40)
        summary.append(f"{'Total':20} {total_time:5.2f} s")
        summary.append(f"Overall Score        {score}/10")
        
        if warnings:
            summary.append("")
            summary.extend(warnings)
            
        summary.append("")
        
        # Print directly to console for visibility, and log at debug level
        summary_text = "\n".join(summary)
        print(summary_text)
        logger.debug(f"Diagnostics:\n{summary_text}")
