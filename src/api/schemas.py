"""Pydantic Schemas for API Requests and Responses"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Speech Recognition Schemas
class TranscribeRequest(BaseModel):
    """Request to transcribe audio"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    sample_rate: int = Field(16000, description="Sample rate of audio in Hz")
    language: str = Field("en-US", description="Language code")


class TranscribeResponse(BaseModel):
    """Response from transcription"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    duration_seconds: float = Field(..., description="Duration of audio")
    timestamp: datetime = Field(default_factory=datetime.now)


# Text-to-Speech Schemas
class SpeakRequest(BaseModel):
    """Request to convert text to speech"""
    text: str = Field(..., description="Text to speak", min_length=1, max_length=1000)
    voice: Optional[str] = Field("default", description="Voice name")
    speed: float = Field(1.0, description="Speech speed (0.5-2.0)")
    language: str = Field("en-US", description="Language code")


class SpeakResponse(BaseModel):
    """Response from TTS"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    duration_seconds: float = Field(..., description="Duration of generated audio")
    voice_used: str = Field(..., description="Voice that was used")


# Conversation Schemas
class Message(BaseModel):
    """A single message in conversation"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request for conversational AI"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    include_context: bool = Field(True, description="Include conversation history")


class ChatResponse(BaseModel):
    """Response from conversational AI"""
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    tokens_used: Optional[int] = Field(None, description="Tokens used")
    backend_used: str = Field(..., description="Backend that generated response")


# Voice Commands Schemas
class CommandExecuteRequest(BaseModel):
    """Request to execute voice command"""
    command: str = Field(..., description="Command name")
    parameters: Optional[dict] = Field(None, description="Command parameters")
    require_confirmation: bool = Field(True, description="Require user confirmation")


class CommandExecuteResponse(BaseModel):
    """Response from command execution"""
    status: str = Field(..., description="'success', 'failed', or 'pending'")
    command: str = Field(..., description="Command executed")
    message: str = Field(..., description="Status message")
    result: Optional[dict] = Field(None, description="Command result")


# Voice Profiles Schemas
class VoiceProfileCreate(BaseModel):
    """Create or update voice profile"""
    user_id: str = Field(..., description="User identifier")
    voice_name: str = Field(..., description="Preferred voice name")
    speech_rate: float = Field(1.0, description="Preferred speech rate")
    volume: float = Field(0.9, description="Preferred volume")


class VoiceProfileResponse(BaseModel):
    """Voice profile response"""
    id: int = Field(..., description="Profile ID")
    user_id: str = Field(..., description="User ID")
    voice_name: str = Field(..., description="Voice name")
    speech_rate: float = Field(..., description="Speech rate")
    volume: float = Field(..., description="Volume")
    created_at: datetime = Field(..., description="Creation timestamp")


# Audio File Schemas
class AudioUploadResponse(BaseModel):
    """Response from audio file upload"""
    file_id: str = Field(..., description="Unique file ID")
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes")
    duration_seconds: float = Field(..., description="Audio duration")


class TranscribeFileRequest(BaseModel):
    """Request to transcribe audio file"""
    file_id: str = Field(..., description="File ID from upload")
    language: Optional[str] = Field("en-US", description="Language code")


class TranscribeFileResponse(BaseModel):
    """Response from file transcription"""
    file_id: str = Field(..., description="File ID")
    text: str = Field(..., description="Transcribed text")
    duration_seconds: float = Field(..., description="Duration")
    word_count: int = Field(..., description="Number of words")
    timestamp: datetime = Field(..., description="Transcription timestamp")


# Settings Schemas
class AudioSettings(BaseModel):
    """Audio configuration"""
    sample_rate: int = Field(16000, description="Sample rate in Hz")
    channels: int = Field(1, description="Number of channels")
    device_index: Optional[int] = Field(None, description="Audio device index")


class APISettings(BaseModel):
    """API configuration with sensitive data"""
    huggingface_api_key: Optional[str] = Field(None, description="HuggingFace API key")
    azure_tts_api_key: Optional[str] = Field(None, description="Azure TTS API key")


class SettingsResponse(BaseModel):
    """Application settings response"""
    audio: AudioSettings = Field(..., description="Audio settings")
    debug: bool = Field(False, description="Debug mode")
    current_backends: dict = Field(..., description="Current backend selection")
    quota_status: dict = Field(..., description="API quota status")


# Status Schemas
class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field(..., description="'healthy' or 'unhealthy'")
    version: str = Field(..., description="App version")
    timestamp: datetime = Field(default_factory=datetime.now)


class SystemStatus(BaseModel):
    """System status response"""
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Uptime in seconds")
    ai_backend: str = Field(..., description="Current AI backend")
    stt_backend: str = Field(..., description="Current STT backend")
    tts_backend: str = Field(..., description="Current TTS backend")
    quota_status: dict = Field(..., description="API quota status")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")


# Error Response
class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.now)
