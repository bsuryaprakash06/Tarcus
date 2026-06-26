import sys
from pathlib import Path

# Configure UTF-8 encoding on standard output/error to prevent UnicodeEncodeErrors with emojis on Windows.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RECORDINGS_DIR = PROJECT_ROOT / "assets" / "recordings"
SOUNDS_DIR = PROJECT_ROOT / "assets" / "sounds"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

INPUT_AUDIO_PATH = RECORDINGS_DIR / "input.wav"

# Audio Recording Settings
SAMPLE_RATE = 16000
CHANNELS = 1
DEFAULT_RECORD_DURATION = 5

# Speech-to-Text Settings
WHISPER_MODEL_NAME = "base"

# Text-to-Speech Settings
VOICE_NAME = "en-US-AriaNeural"
VOICE_RATE = "+0%"
VOICE_VOLUME = "+0%"

# Ollama LLM Settings
OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen3:4b"

# Ensure runtime directories exist
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
