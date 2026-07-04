import numpy as np
from src.utils.logger import get_logger
from src.utils.settings import ENABLE_METRICS

logger = get_logger("metrics")

class MetricsService:
    """
    Singleton service that tracks runtime statistics and raw measurements.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        self.planner_latencies = []
        self.execution_latencies = []
        self.tool_usage = {}
        self.successful_executions = 0
        self.failed_executions = 0
        self.total_transcriptions = 0
        self.corrected_terms = {}
        self.intent_counts = {}
        self.classifier_latencies = []
        self.response_lengths = []
        self.speech_durations = []
        self.formatter_latencies = []
        self.shortened_responses = 0
        self.total_responses = 0
        
    def record_planner_latency(self, latency: float) -> None:
        if ENABLE_METRICS:
            self.planner_latencies.append(latency)
            
    def record_execution_latency(self, latency: float) -> None:
        if ENABLE_METRICS:
            self.execution_latencies.append(latency)
            
    def record_tool_usage(self, tool_name: str, success: bool) -> None:
        if not ENABLE_METRICS:
            return
            
        self.tool_usage[tool_name] = self.tool_usage.get(tool_name, 0) + 1
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1

    def record_normalization(self, was_normalized: bool, terms: list[str]) -> None:
        if not ENABLE_METRICS:
            return
            
        self.total_transcriptions += 1
        if was_normalized:
            self.normalized_transcriptions += 1
            for term in terms:
                self.corrected_terms[term] = self.corrected_terms.get(term, 0) + 1

    def record_intent(self, intent_name: str, latency: float) -> None:
        if not ENABLE_METRICS:
            return
            
        self.intent_counts[intent_name] = self.intent_counts.get(intent_name, 0) + 1
        self.classifier_latencies.append(latency)

    def record_formatting(self, original_length: int, final_length: int, duration: float, latency: float) -> None:
        if not ENABLE_METRICS:
            return
            
        self.total_responses += 1
        self.response_lengths.append(final_length)
        self.speech_durations.append(duration)
        self.formatter_latencies.append(latency)
        
        if final_length < original_length:
            self.shortened_responses += 1

    def _compute_stats(self, data: list) -> dict:
        """Helper to compute statistics for a given raw array."""
        if not data:
            return {"average": 0.0, "median": 0.0, "p95": 0.0, "min": 0.0, "max": 0.0}
            
        arr = np.array(data)
        return {
            "average": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "p95": float(np.percentile(arr, 95)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr))
        }

    def print_summary(self) -> None:
        """Prints the summary report of all tracked metrics."""
        if not ENABLE_METRICS:
            return
            
        planner_stats = self._compute_stats(self.planner_latencies)
        exec_stats = self._compute_stats(self.execution_latencies)
        classifier_stats = self._compute_stats(self.classifier_latencies)
        
        total_exec = self.successful_executions + self.failed_executions
        success_rate = (self.successful_executions / total_exec * 100) if total_exec > 0 else 0.0
        failure_rate = (self.failed_executions / total_exec * 100) if total_exec > 0 else 0.0
        
        normalization_rate = (self.normalized_transcriptions / self.total_transcriptions * 100) if self.total_transcriptions > 0 else 0.0
        summary = [
            "",
            "Metrics Summary",
            "-" * 20,
            "Response Formatter:",
            f"  Avg Latency: {self._compute_stats(self.formatter_latencies)['average']:.2f} s",
            f"  Avg Duration:{self._compute_stats(self.speech_durations)['average']:.2f} s",
            f"  Shortened:   {(self.shortened_responses / self.total_responses * 100) if self.total_responses > 0 else 0:.1f}%",
            "",
            "Intent Classifier:",
            f"  Average: {classifier_stats['average']:.2f} s",
            f"  Median:  {classifier_stats['median']:.2f} s",
            "",
            "Planner:",
            f"  Average: {planner_stats['average']:.2f} s",
            f"  Median:  {planner_stats['median']:.2f} s",
            f"  P95:     {planner_stats['p95']:.2f} s",
            "",
            "Execution:",
            f"  Average: {exec_stats['average']:.2f} s",
            f"  Median:  {exec_stats['median']:.2f} s",
            "",
            "Overall:",
            f"  Success Rate: {success_rate:.1f}%",
            f"  Failure Rate: {failure_rate:.1f}%",
            f"  Normalization Rate: {normalization_rate:.1f}%",
            "-" * 20
        ]
        
        if self.intent_counts:
            summary.append("Intent Distribution:")
            total_intents = sum(self.intent_counts.values())
            for intent, count in sorted(self.intent_counts.items(), key=lambda x: x[1], reverse=True):
                pct = (count / total_intents * 100) if total_intents > 0 else 0
                summary.append(f"  {intent}: {count} ({pct:.1f}%)")
                
            fallback_freq = (self.intent_counts.get("UNKNOWN", 0) / total_intents * 100) if total_intents > 0 else 0
            mixed_freq = (self.intent_counts.get("MIXED", 0) / total_intents * 100) if total_intents > 0 else 0
            summary.append(f"  Fallback Frequency: {fallback_freq:.1f}%")
            summary.append(f"  Mixed Intent Frequency: {mixed_freq:.1f}%")
            summary.append("-" * 20)
            
        summary.append("Tool Usage:")
        for tool, count in sorted(self.tool_usage.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"  {tool}: {count}")
            
        if self.corrected_terms:
            summary.append("-" * 20)
            summary.append("Most Corrected Terms:")
            for term, count in sorted(self.corrected_terms.items(), key=lambda x: x[1], reverse=True)[:5]:
                summary.append(f"  {term}: {count}")
            
        summary.append("")
        
        summary_text = "\n".join(summary)
        print(summary_text)
        logger.debug(f"Metrics Dump:\n{summary_text}")
