import sys
from rich.console import Console
from src.utils.logger import get_logger
from src.utils.enums import AssistantStatus
from src.utils.exceptions import VoiceAssistantError
from src.utils.startup import run_startup_checks
from src.services.voice_service import VoiceService
from src.services.tts_service import TTSService
from src.services.response_service import ResponseService, ResponseMode
from src.models.transcription import TranscriptionResult

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

def understand(transcription_text: str) -> str:
    """
    Step 2: understand() - determines what should happen and formulates responses.
    (Currently routes directly to ResponseService; in Milestone 3, this will call the LLM Planner).
    """
    return response_service.formulate_response(transcription_text, ResponseMode.SUCCESS)

def respond(response_text: str) -> None:
    """
    Step 3: respond() - outputs response to console and speaks it using the text-to-speech engine.
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
            
            # 2. Understand
            status = AssistantStatus.PROCESSING
            response_text = understand(result.text)
            
            # 3. Respond
            status = AssistantStatus.COMPLETED
            respond(response_text)
            
            # Ready again
            status = AssistantStatus.IDLE
            console.print()
            
    except VoiceAssistantError as vae:
        status = AssistantStatus.ERROR
        console.print(f"\n[bold red]Error: {vae}[/bold red]")
        sys.exit(1)
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
