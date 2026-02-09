"""Pyttsx3 Offline Text-to-Speech Engine"""

import pyttsx3
import numpy as np
from typing import Optional, List
import io
import wave

from ...config.settings import get_settings
from ...config.logger import get_logger

logger = get_logger(__name__)


class Pyttsx3Engine:
    """Pyttsx3 offline text-to-speech engine"""

    def __init__(self):
        """Initialize Pyttsx3 engine"""
        settings = get_settings()
        self.tts_settings = settings.text_to_speech

        self.engine = None
        self.is_initialized = False
        self.available_voices = []

        # Initialize
        self._initialize_engine()

    def _initialize_engine(self) -> bool:
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()

            # Configure engine
            self.engine.setProperty("rate", self.tts_settings.pyttsx3_rate)
            self.engine.setProperty("volume", self.tts_settings.pyttsx3_volume)

            # Get available voices
            self.available_voices = self.engine.getProperty("voices")

            # Set voice
            if len(self.available_voices) > self.tts_settings.pyttsx3_voice_index:
                self.engine.setProperty("voice", self.available_voices[self.tts_settings.pyttsx3_voice_index].id)

            self.is_initialized = True
            logger.info(f"Pyttsx3 engine initialized with {len(self.available_voices)} voices")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Pyttsx3: {e}")
            return False

    def list_voices(self) -> List[dict]:
        """List available voices"""
        voices = []
        for i, voice in enumerate(self.available_voices):
            voices.append({
                "index": i,
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages
            })
        return voices

    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Speak text

        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
        """
        if not self.is_initialized or not self.engine:
            logger.error("Pyttsx3 engine not initialized")
            return False

        try:
            self.engine.say(text)
            self.engine.runAndWait()
            logger.debug(f"Spoke text: {text[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            return False

    def speak_to_file(self, text: str, file_path: str) -> bool:
        """
        Save speech to audio file

        Args:
            text: Text to speak
            file_path: Output file path
        """
        if not self.is_initialized or not self.engine:
            logger.error("Pyttsx3 engine not initialized")
            return False

        try:
            # Save to file
            self.engine.save_to_file(text, file_path)
            self.engine.runAndWait()

            logger.info(f"Saved speech to: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving speech to file: {e}")
            return False

    def set_voice(self, voice_index: int) -> bool:
        """Set active voice by index"""
        try:
            if voice_index < len(self.available_voices):
                self.engine.setProperty("voice", self.available_voices[voice_index].id)
                logger.info(f"Voice set to: {self.available_voices[voice_index].name}")
                return True
            else:
                logger.error(f"Voice index {voice_index} out of range")
                return False

        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False

    def set_rate(self, rate: int) -> bool:
        """Set speech rate (words per minute)"""
        try:
            self.engine.setProperty("rate", rate)
            logger.debug(f"Speech rate set to: {rate}")
            return True
        except Exception as e:
            logger.error(f"Error setting rate: {e}")
            return False

    def set_volume(self, volume: float) -> bool:
        """Set volume (0.0-1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty("volume", volume)
            logger.debug(f"Volume set to: {volume}")
            return True
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False

    def get_status(self) -> dict:
        """Get engine status"""
        return {
            "engine": "pyttsx3",
            "initialized": self.is_initialized,
            "available_voices": len(self.available_voices),
            "rate": self.tts_settings.pyttsx3_rate if self.is_initialized else None,
            "volume": self.tts_settings.pyttsx3_volume if self.is_initialized else None
        }

    def __del__(self):
        """Cleanup"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


# Global instance
_pyttsx3_instance: Optional[Pyttsx3Engine] = None


def get_pyttsx3_engine() -> Pyttsx3Engine:
    """Get or create Pyttsx3 engine instance"""
    global _pyttsx3_instance
    if _pyttsx3_instance is None:
        _pyttsx3_instance = Pyttsx3Engine()
    return _pyttsx3_instance
