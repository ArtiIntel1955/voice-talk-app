"""Application Settings Configuration using Pydantic"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class AudioSettings(BaseSettings):
    """Audio capture and playback settings"""
    sample_rate: int = Field(16000, description="Audio sample rate in Hz")
    channels: int = Field(1, description="Number of audio channels (mono)")
    chunk_size: int = Field(1024, description="Audio chunk size for processing")
    device_index: Optional[int] = Field(None, description="Audio device index, None for default")

    class Config:
        env_prefix = "AUDIO_"


class SpeechRecognitionSettings(BaseSettings):
    """Speech recognition settings"""
    primary: str = Field("vosk", description="Primary STT engine: vosk, sherpa-onnx, huggingface")
    offline_enabled: bool = Field(True, description="Enable offline speech recognition")
    online_enabled: bool = Field(True, description="Enable online speech recognition")
    timeout_seconds: int = Field(30, description="Timeout for API calls")
    confidence_threshold: float = Field(0.5, description="Confidence threshold for recognition")
    vosk_model_path: str = Field("./models/vosk_models/model", description="Path to Vosk model")
    huggingface_model_id: str = Field("openai/whisper-small", description="Hugging Face model ID")
    huggingface_api_key: Optional[str] = Field(None, description="Hugging Face API key")

    class Config:
        env_prefix = "STT_"


class TextToSpeechSettings(BaseSettings):
    """Text-to-speech settings"""
    primary: str = Field("pyttsx3", description="Primary TTS engine: pyttsx3, vits, azure")
    offline_enabled: bool = Field(True, description="Enable offline TTS")
    online_enabled: bool = Field(True, description="Enable online TTS")
    pyttsx3_voice_index: int = Field(0, description="Pyttsx3 voice index")
    pyttsx3_rate: int = Field(150, description="Pyttsx3 speech rate")
    pyttsx3_volume: float = Field(0.9, description="Pyttsx3 volume (0.0-1.0)")
    azure_api_key: Optional[str] = Field(None, description="Azure TTS API key")
    azure_region: str = Field("eastus", description="Azure region")

    class Config:
        env_prefix = "TTS_"


class ConversationalAISettings(BaseSettings):
    """Conversational AI settings"""
    primary: str = Field("huggingface", description="Primary AI engine: huggingface, ollama")
    offline_enabled: bool = Field(False, description="Enable local Ollama")
    online_enabled: bool = Field(True, description="Enable cloud API")
    ollama_base_url: str = Field("http://localhost:11434", description="Ollama server URL")
    ollama_model: str = Field("mistral", description="Ollama model name")
    ollama_temperature: float = Field(0.7, description="Temperature for response generation")
    ollama_context_length: int = Field(4096, description="Context window size")
    huggingface_model_id: str = Field("HuggingFaceH4/zephyr-7b-beta", description="Hugging Face model ID")
    huggingface_api_key: Optional[str] = Field(None, description="Hugging Face API key")

    class Config:
        env_prefix = "AI_"


class VoiceCommandsSettings(BaseSettings):
    """Voice command settings"""
    enabled: bool = Field(True, description="Enable voice command recognition")
    confirmation_required: bool = Field(True, description="Require confirmation before execution")
    log_all_commands: bool = Field(True, description="Log all executed commands")

    class Config:
        env_prefix = "COMMANDS_"


class DatabaseSettings(BaseSettings):
    """Database settings"""
    db_type: str = Field("sqlite", description="Database type")
    db_path: str = Field("./data/conversations.db", description="Database file path")
    backup_interval_hours: int = Field(24, description="Backup interval in hours")

    class Config:
        env_prefix = "DB_"


class CacheSettings(BaseSettings):
    """Cache settings"""
    enabled: bool = Field(True, description="Enable caching")
    ttl_seconds: int = Field(3600, description="Cache TTL in seconds")
    max_size_mb: int = Field(500, description="Maximum cache size in MB")

    class Config:
        env_prefix = "CACHE_"


class AccessibilitySettings(BaseSettings):
    """Accessibility settings"""
    screen_reader_enabled: bool = Field(False, description="Enable screen reader support")
    high_contrast: bool = Field(False, description="Enable high contrast mode")
    font_size: int = Field(12, description="Default font size in points")

    class Config:
        env_prefix = "A11Y_"


class LoggingSettings(BaseSettings):
    """Logging settings"""
    level: str = Field("INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    log_file: str = Field("./data/logs/app.log", description="Log file path")
    max_size_mb: int = Field(100, description="Maximum log file size in MB")
    backup_count: int = Field(5, description="Number of backup log files to keep")

    class Config:
        env_prefix = "LOG_"


class ApplicationSettings(BaseSettings):
    """Top-level application settings"""
    app_name: str = Field("Voice Talk Application", description="Application name")
    version: str = Field("0.1.0", description="Application version")
    debug: bool = Field(False, description="Enable debug mode")
    host: str = Field("127.0.0.1", description="Server host")
    port: int = Field(8000, description="Server port")

    # Nested settings
    audio: AudioSettings = Field(default_factory=AudioSettings)
    speech_recognition: SpeechRecognitionSettings = Field(default_factory=SpeechRecognitionSettings)
    text_to_speech: TextToSpeechSettings = Field(default_factory=TextToSpeechSettings)
    conversational_ai: ConversationalAISettings = Field(default_factory=ConversationalAISettings)
    voice_commands: VoiceCommandsSettings = Field(default_factory=VoiceCommandsSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    accessibility: AccessibilitySettings = Field(default_factory=AccessibilitySettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings: Optional[ApplicationSettings] = None


def get_settings() -> ApplicationSettings:
    """Get or create application settings instance"""
    global _settings
    if _settings is None:
        _settings = ApplicationSettings()
    return _settings


def reload_settings() -> ApplicationSettings:
    """Reload settings from environment and config files"""
    global _settings
    _settings = ApplicationSettings()
    return _settings
