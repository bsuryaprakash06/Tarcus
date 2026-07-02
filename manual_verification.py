import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Ensure we load the environment correctly
load_dotenv()

from src.utils.logger import get_logger
from src.tools.registry import ToolRegistry
from src.brain.prompt_builder import PromptBuilder
from src.brain.planner import Planner

logger = get_logger("verification")

def run_verification():
    """
    Manually verifies that the Planner produces valid ExecutionPlans 
    without executing the actual Windows commands.
    """
    print("\n" + "="*50)
    print("🧠 TARCUS PLANNER MANUAL VERIFICATION 🧠")
    print("="*50)

    # Initialize the planner (it will use your configured LLM provider in .env)
    try:
        planner = Planner()
    except Exception as e:
        print(f"\n[!] Failed to initialize Planner: {e}")
        print("Please ensure your LLM provider is properly configured in your .env file.")
        sys.exit(1)

    commands = [
        "Open Notepad",
        "Create a folder called Physics",
        "Search Python tutorials",
        "Open Calculator"
    ]

    for index, cmd in enumerate(commands, 1):
        print(f"\n[{index}/{len(commands)}] Command: '{cmd}'")
        print("-" * 50)
        
        try:
            # The planner encapsulates the Provider call and the 3-stage validation
            plan = planner.plan(cmd)
            
            print("✅ Verification: PASSED")
            print("✅ Status: Fully Validated ExecutionPlan created successfully.")
            print("\n📋 Validated JSON ExecutionPlan:\n")
            print(json.dumps(json.loads(plan.model_dump_json()), indent=4))
            
        except Exception as e:
            print("❌ Verification: FAILED")
            print(f"Error encountered during planning/validation:\n{e}")
        
        print("-" * 50)
        
    print("\n✅ Manual Verification Completed.\n")

if __name__ == "__main__":
    run_verification()
