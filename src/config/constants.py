"""Application Constants"""

# Audio processing constants
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1
DEFAULT_CHUNK_SIZE = 1024
AUDIO_FORMATS = ("wav", "mp3", "flac", "ogg", "m4a")

# API paths
API_PREFIX = "/api"
API_VERSION = "v1"
SPEECH_RECOGNITION_ENDPOINT = f"{API_PREFIX}/speech"
TEXT_TO_SPEECH_ENDPOINT = f"{API_PREFIX}/voice"
CONVERSATION_ENDPOINT = f"{API_PREFIX}/conversation"
COMMANDS_ENDPOINT = f"{API_PREFIX}/commands"
AUDIO_ENDPOINT = f"{API_PREFIX}/audio"
SETTINGS_ENDPOINT = f"{API_PREFIX}/settings"

# Model paths
VOSK_MODEL_PATH = "./models/vosk_models/model"
OLLAMA_BASE_URL = "http://localhost:11434"

# Cache settings
DEFAULT_CACHE_TTL_SECONDS = 3600
DEFAULT_CACHE_MAX_SIZE_MB = 500

# Database
DEFAULT_DB_PATH = "./data/conversations.db"

# Logging
DEFAULT_LOG_FILE = "./data/logs/app.log"
DEFAULT_LOG_LEVEL = "INFO"

# Voice command settings
MIN_CONFIDENCE_THRESHOLD = 0.5
MAX_CONFIDENCE_THRESHOLD = 1.0

# Feature flags
ENABLE_VOICE_COMMANDS = True
REQUIRE_COMMAND_CONFIRMATION = True
ENABLE_SCREEN_READER = False

# Timeout settings
DEFAULT_API_TIMEOUT_SECONDS = 30
DEFAULT_NETWORK_CHECK_INTERVAL_SECONDS = 30

# Message limits
MAX_MESSAGE_LENGTH = 10000
MIN_MESSAGE_LENGTH = 1

# Rate limiting (for free API usage)
HUGGINGFACE_DAILY_LIMIT = 1000  # Approximate daily limit
HUGGINGFACE_HOURLY_LIMIT = 100
