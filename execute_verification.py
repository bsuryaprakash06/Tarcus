import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure we load the environment correctly
load_dotenv()

# Explicitly override DRY_RUN before other imports resolve it where possible
import os
os.environ["DRY_RUN"] = "True"

from src.utils.logger import get_logger
from src.brain.planner import Planner
from src.services.executor_service import ExecutorService
from src.services.response_service import ResponseService
import src.utils.settings as settings

# Force setting to True in memory for modules that already imported it
settings.DRY_RUN = True

logger = get_logger("execute_verification")

def run_executor_verification():
    """
    Manually verifies that the Executor processes ExecutionPlans and
    returns proper ToolResults in DRY_RUN mode.
    """
    print("\n" + "="*50)
    print("🚀 TARCUS EXECUTOR VERIFICATION (DRY RUN) 🚀")
    print("="*50)

    try:
        planner = Planner()
        executor = ExecutorService()
        responder = ResponseService()
    except Exception as e:
        print(f"\n[!] Failed to initialize services: {e}")
        sys.exit(1)

    commands = [
        "Open Notepad",
        "Create a folder called Physics",
        "Search Python tutorials"
    ]

    for index, cmd in enumerate(commands, 1):
        print(f"\n[{index}/{len(commands)}] Command: '{cmd}'")
        print("-" * 50)
        
        try:
            # 1. Plan
            plan = planner.plan(cmd)
            
            # 2. Execute
            results = executor.execute_plan(plan)
            
            # 3. Respond
            response = responder.formulate_execution_response(results)
            
            print(f"🗣️  Tarcus Voice Response: {response}")
            
            for res in results:
                print(f"    - Tool: {res.tool_name} | Success: {res.success} | Duration: {res.duration:.2f}s")
            
        except Exception as e:
            print("❌ Verification: FAILED")
            print(f"Error encountered:\n{e}")
        
        print("-" * 50)
        
    print("\n✅ Execution Verification Completed.\n")
    print("To test live execution (without DRY_RUN), set DRY_RUN=false in your .env file and run standard execution logic.\n")

if __name__ == "__main__":
    run_executor_verification()
