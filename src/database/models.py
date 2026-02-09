"""SQLAlchemy ORM Models for Database"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class ConversationSession(Base):
    """Model for conversation sessions"""
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    metadata_entries = relationship("SessionMetadata", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ConversationSession(id={self.id}, session_id={self.session_id}, user_id={self.user_id})>"


class Message(Base):
    """Model for messages in a conversation"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    confidence = Column(Float, nullable=True)  # For STT confidence
    metadata = Column(Text, nullable=True)  # JSON metadata

    # Relationships
    session = relationship("ConversationSession", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role})>"


class VoiceProfile(Base):
    """Model for voice profiles and settings"""
    __tablename__ = "voice_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    voice_name = Column(String(100), nullable=False)
    preferred_language = Column(String(10), default="en-US")
    speech_rate = Column(Float, default=1.0)
    volume = Column(Float, default=0.9)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<VoiceProfile(id={self.id}, user_id={self.user_id})>"


class CommandHistory(Base):
    """Model for executed voice commands history"""
    __tablename__ = "command_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    command = Column(String(500), nullable=False)
    parameters = Column(Text, nullable=True)  # JSON
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'pending'
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_ms = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<CommandHistory(id={self.id}, command={self.command}, status={self.status})>"


class AudioFile(Base):
    """Model for processed audio files"""
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=False)
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_format = Column(String(20), nullable=False)  # wav, mp3, etc.
    duration_seconds = Column(Float, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    transcription_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    transcription_text = Column(Text, nullable=True)
    transcription_json = Column(Text, nullable=True)  # JSON with timestamps

    def __repr__(self):
        return f"<AudioFile(id={self.id}, file_id={self.file_id}, format={self.file_format})>"


class SessionMetadata(Base):
    """Model for session metadata and tracking"""
    __tablename__ = "session_metadata"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("ConversationSession", back_populates="metadata_entries")

    def __repr__(self):
        return f"<SessionMetadata(id={self.id}, key={self.key})>"


class APIQuotaTracker(Base):
    """Model for tracking API quota usage for smart model switching"""
    __tablename__ = "api_quota_tracker"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(50), unique=True, index=True, nullable=False)  # huggingface, azure, etc.
    daily_calls = Column(Integer, default=0)
    daily_limit = Column(Integer, nullable=False)
    last_reset_date = Column(DateTime(timezone=True), server_default=func.now())
    is_quota_exceeded = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<APIQuotaTracker(id={self.id}, service={self.service_name}, calls={self.daily_calls}/{self.daily_limit})>"


class CacheEntry(Base):
    """Model for caching responses"""
    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(500), unique=True, index=True, nullable=False)
    cache_value = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accessed_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<CacheEntry(id={self.id}, key={self.cache_key})>"
