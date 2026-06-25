import sys
# pyrefly: ignore [missing-import]
from rich.console import Console

# Configure UTF-8 encoding on standard output/error to prevent UnicodeEncodeErrors with emojis on Windows.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.utils.logger import get_logger
from src.utils.enums import AssistantStatus
from src.utils.exceptions import VoiceAssistantError
from src.utils.startup import run_startup_checks
from src.services.voice_service import VoiceService

logger = get_logger("main")
console = Console()

def print_banner():
    console.print("[bold cyan]=================================[/bold cyan]")
    console.print("[bold cyan]Voice Assistant[/bold cyan]")
    console.print("[bold cyan]=================================[/bold cyan]")
    console.print()

def main():
    console.print("[yellow]Initializing components, please wait...[/yellow]")
    if not run_startup_checks():
        console.print("\n[bold red]Startup checks failed! Please check the logs at logs/voice_assistant.log.[/bold red]")
        sys.exit(1)
        
    print_banner()
    
    status = AssistantStatus.IDLE
    voice_service = VoiceService()
    
    try:
        console.input("[bold green]Press Enter to Speak...[/bold green]")
        
        status = AssistantStatus.RECORDING
        console.print("[bold red]🎤 Recording...[/bold red]")
        result = voice_service.listen()
        
        status = AssistantStatus.COMPLETED
        console.print()
        console.print("[bold green]✅ You said:[/bold green]")
        console.print(f"[bold white]{result.text}[/bold white]")
        
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
