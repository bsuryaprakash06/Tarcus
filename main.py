import sys
from rich.console import Console
from src.utils.logger import get_logger
from src.utils.enums import AssistantStatus
from src.utils.exceptions import VoiceAssistantError
from src.utils.startup import run_startup_checks
from src.services.voice_service import VoiceService
from src.services.tts_service import TTSService
from src.services.response_service import ResponseService, ResponseMode
from src.services.llm_service import LLMService
from src.services.executor_service import ExecutorService
from src.safety.validator import SafetyValidator, SafetyError
from src.models.transcription import TranscriptionResult
from src.models.plan import ExecutionPlan, ToolResult

# Configure UTF-8 encoding on standard output/error to prevent UnicodeEncodeErrors with emojis on Windows.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = get_logger("main")
console = Console()

# Instantiate services globally
voice_service = VoiceService()
tts_service = TTSService()
response_service = ResponseService()
llm_service = LLMService()
executor_service = ExecutorService()
safety_validator = SafetyValidator()

def print_banner():
    console.print("[bold cyan]=================================[/bold cyan]")
    console.print("[bold cyan]Tarcus[/bold cyan]")
    console.print("[bold cyan]=================================[/bold cyan]")
    console.print()

def listen() -> TranscriptionResult:
    """
    Step 1: listen() - records from microphone and runs transcription using Whisper.
    """
    console.input("[bold green]Press Enter to Speak...[/bold green]")
    console.print("[bold red]🎤 Recording...[/bold red]")
    return voice_service.listen()

def understand(user_command: str) -> ExecutionPlan:
    """
    Step 2: understand() - generates a structured execution plan from the user command using the LLM Planner.
    """
    console.print("[bold yellow]⚙️ Processing...[/bold yellow]")
    return llm_service.generate_plan(user_command)

def validate_safety(plan: ExecutionPlan) -> bool:
    """
    Step 2.5: validate_safety() - validates the plan safety levels.
    Raises SafetyError if any restricted/blocked tools are requested.
    Returns True if any confirm-required tools are requested, otherwise False.
    """
    return safety_validator.validate_plan(plan)

def execute(plan: ExecutionPlan) -> list[ToolResult]:
    """
    Step 3: execute() - runs the sequence of planned tool calls.
    """
    return executor_service.execute_plan(plan)

def respond(response_text: str) -> None:
    """
    Step 4: respond() - outputs response to console and speaks it using the text-to-speech engine.
    """
    console.print()
    console.print("[bold magenta]Tarcus:[/bold magenta]")
    console.print(f"[bold white]{response_text}[/bold white]")
    tts_service.say(response_text)

def main():
    console.print("[yellow]Initializing components, please wait...[/yellow]")
    if not run_startup_checks():
        console.print("\n[bold red]Startup checks failed! Please check the logs at logs/voice_assistant.log.[/bold red]")
        sys.exit(1)
        
    print_banner()
    
    status = AssistantStatus.IDLE
    
    try:
        while True:
            # 1. Listen
            status = AssistantStatus.RECORDING
            result = listen()
            
            # Print transcribed text
            console.print()
            console.print("[bold green]✅ You said:[/bold green]")
            console.print(f"[bold white]{result.text if result.text else '(Silence)'}[/bold white]")
            
            if not result.text.strip():
                # Handle empty input
                response_text = response_service.formulate_response("", ResponseMode.SUCCESS)
                respond(response_text)
                status = AssistantStatus.IDLE
                console.print()
                continue
            
            try:
                # 2. Understand
                status = AssistantStatus.PROCESSING
                plan = understand(result.text)
                
                # 2.5. Safety check
                needs_confirm = validate_safety(plan)
                
                if needs_confirm:
                    console.print("[bold yellow]⚠️ Safety Warning: This action requires user confirmation.[/bold yellow]")
                    confirm = console.input("[bold yellow]Do you want to proceed? (y/n): [/bold yellow]").strip().lower()
                    if confirm not in ("y", "yes"):
                        console.print("[bold yellow]Execution cancelled for safety.[/bold yellow]")
                        response_text = response_service.formulate_response("I cancelled the action for safety.", ResponseMode.WARNING)
                        respond(response_text)
                        status = AssistantStatus.IDLE
                        console.print()
                        continue
                
                # 3. Execute
                status = AssistantStatus.PROCESSING
                results = execute(plan)
                
                # 4. Respond
                status = AssistantStatus.COMPLETED
                response_text = response_service.formulate_execution_response(results)
                respond(response_text)
                
            except SafetyError as se:
                status = AssistantStatus.ERROR
                console.print(f"\n[bold red]Safety Error: {se}[/bold red]")
                response_text = response_service.formulate_response(str(se), ResponseMode.ERROR)
                respond(response_text)
            except Exception as e:
                status = AssistantStatus.ERROR
                logger.error(f"Error during planning or execution: {e}")
                console.print(f"\n[bold red]Error: {e}[/bold red]")
                response_text = response_service.formulate_response("I encountered an issue while processing your command.", ResponseMode.ERROR)
                respond(response_text)
            
            # Ready again
            status = AssistantStatus.IDLE
            console.print()
            
    except KeyboardInterrupt:
        status = AssistantStatus.IDLE
        console.print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        status = AssistantStatus.ERROR
        console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
