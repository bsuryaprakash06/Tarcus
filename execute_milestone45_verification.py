import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure we load the environment correctly
load_dotenv()
os.environ["DRY_RUN"] = "True"
os.environ["DEBUG_MODE"] = "True"

import src.utils.settings as settings
settings.DRY_RUN = True
settings.DEBUG_MODE = True

from src.utils.logger import get_logger
from src.brain.planner import Planner
from src.services.executor_service import ExecutorService
from src.services.metrics_service import MetricsService
from src.services.diagnostics_service import DiagnosticsService
from src.services.history_service import CommandHistoryService

logger = get_logger("execute_verification")

def run_executor_verification():
    """
    Manually verifies that the Executor processes ExecutionPlans and
    returns proper ToolResults in DRY_RUN mode for Milestone 4.5.
    """
    print("\n" + "="*50)
    print("🚀 TARCUS M4.5 VERIFICATION (DRY RUN) 🚀")
    print("="*50)

    try:
        planner = Planner()
        executor = ExecutorService()
        metrics = MetricsService()
        history = CommandHistoryService()
        diagnostics = DiagnosticsService()
    except Exception as e:
        print(f"\n[!] Failed to initialize services: {e}")
        sys.exit(1)

    commands = [
        "Open Notepad",
        "Search chat GPT",
        "Take a screenshot",
        "Copy 'Hello World' to the clipboard",
        "Read my clipboard",
        "Close Notepad",
        "Rename report.txt to final_report.txt",
        "Move final_report.txt to the documents folder",
        "Delete the temp file"
    ]

    for index, cmd in enumerate(commands, 1):
        print(f"\n[{index}/{len(commands)}] Command: '{cmd}'")
        print("-" * 50)
        
        try:
            diagnostics.start_timer("Planner")
            plan = planner.plan(cmd)
            diagnostics.stop_timer("Planner")
            
            # Start execution timer
            diagnostics.start_timer("Execution")
            
            # Create a history record
            execution_id = os.urandom(4).hex()
            record = history.create_record(execution_id, cmd)
            record.plan = plan
            
            # Execute
            results = executor.execute_plan(plan, session_id="test_session")
            
            record.tool_results = results
            diagnostics.stop_timer("Execution")
            
            for res in results:
                print(f"    - Tool: {res.tool_name} | Success: {res.success} | Duration: {res.duration:.2f}s")
                print(f"      Message: {res.message}")
            
        except Exception as e:
            import traceback
            print("❌ Verification: FAILED")
            print("Error encountered:")
            traceback.print_exc()
        
        print("-" * 50)
        
    print("\n✅ Verification Completed.\n")
    
    # Print Diagnostics & Metrics
    print("\n=== DIAGNOSTICS & METRICS REPORT ===")
    diagnostics.print_summary()
    metrics.print_summary()

if __name__ == "__main__":
    run_executor_verification()
