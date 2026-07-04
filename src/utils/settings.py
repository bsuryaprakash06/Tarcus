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

# LLM Provider Configuration
import os
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv(PROJECT_ROOT / ".env")

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "groq").lower()
MODEL_NAME = os.environ.get("MODEL_NAME", "")
API_KEY = os.environ.get("API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = os.environ.get("BASE_URL", "")

# Feature Flags
DRY_RUN = os.environ.get("DRY_RUN", "False").lower() == "true"
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() == "true"
ENABLE_DIAGNOSTICS = os.environ.get("ENABLE_DIAGNOSTICS", "True").lower() == "true"
ENABLE_METRICS = os.environ.get("ENABLE_METRICS", "True").lower() == "true"
VOICE_ACTIVITY_ENABLED = os.environ.get("VOICE_ACTIVITY_ENABLED", "True").lower() == "true"

# Audio Recording & VAD Constants
MAX_RECORDING_SECONDS = float(os.environ.get("MAX_RECORDING_SECONDS", "10.0"))
SILENCE_TIMEOUT_SECONDS = float(os.environ.get("SILENCE_TIMEOUT_SECONDS", "1.25"))
INITIAL_SILENCE_TIMEOUT = float(os.environ.get("INITIAL_SILENCE_TIMEOUT", "3.0"))
MIN_SPEECH_SECONDS = float(os.environ.get("MIN_SPEECH_SECONDS", "0.5"))
MIC_ENERGY_THRESHOLD = float(os.environ.get("MIC_ENERGY_THRESHOLD", "0.05"))

# Speech Normalization Settings
ENABLE_SPEECH_NORMALIZATION = os.environ.get("ENABLE_SPEECH_NORMALIZATION", "True").lower() == "true"
ENABLE_ALIAS_EXPANSION = os.environ.get("ENABLE_ALIAS_EXPANSION", "True").lower() == "true"
ENABLE_BRAND_NORMALIZATION = os.environ.get("ENABLE_BRAND_NORMALIZATION", "True").lower() == "true"
ENABLE_TECHNICAL_NORMALIZATION = os.environ.get("ENABLE_TECHNICAL_NORMALIZATION", "True").lower() == "true"
ENABLE_OS_NORMALIZATION = os.environ.get("ENABLE_OS_NORMALIZATION", "True").lower() == "true"

# Intent Router Settings
ENABLE_INTENT_ROUTER = os.environ.get("ENABLE_INTENT_ROUTER", "True").lower() == "true"
INTENT_HIGH_CONFIDENCE = float(os.environ.get("INTENT_HIGH_CONFIDENCE", "0.90"))
INTENT_LOW_CONFIDENCE = float(os.environ.get("INTENT_LOW_CONFIDENCE", "0.60"))

# Formatter Settings
ENABLE_SPEECH_OPTIMIZATION = os.environ.get("ENABLE_SPEECH_OPTIMIZATION", "True").lower() == "true"
DEFAULT_RESPONSE_STYLE = os.environ.get("DEFAULT_RESPONSE_STYLE", "friendly")

# Automatic Fallback: If Groq is primary but no valid API key is present, fallback to local Ollama (Llama)
if LLM_PROVIDER == "groq":
    _active_key = GROQ_API_KEY or API_KEY
    if not _active_key or "your_" in _active_key.lower():
        LLM_PROVIDER = "ollama"

# Ensure runtime directories exist
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
