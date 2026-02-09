"""Vosk Offline Speech Recognition Engine"""

import json
from pathlib import Path
from typing import Optional, Tuple
import subprocess

from vosk import Model, KaldiRecognizer
import pyaudio

from ...config.settings import get_settings
from ...config.logger import get_logger

logger = get_logger(__name__)


class VoskEngine:
    """Vosk offline speech recognition engine"""

    def __init__(self):
        """Initialize Vosk engine"""
        settings = get_settings()
        self.model_path = settings.speech_recognition.vosk_model_path
        self.sample_rate = settings.audio.sample_rate
        self.confidence_threshold = settings.speech_recognition.confidence_threshold

        self.model: Optional[Model] = None
        self.recognizer: Optional[KaldiRecognizer] = None
        self.is_initialized = False

        # Try to initialize
        self._initialize_model()

    def _initialize_model(self) -> bool:
        """Initialize Vosk model"""
        try:
            if not Path(self.model_path).exists():
                logger.warning(f"Vosk model not found at {self.model_path}")
                logger.info("Please download model from: https://alphacephei.com/vosk/models")
                return False

            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.is_initialized = True

            logger.info(f"Vosk engine initialized with model: {self.model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Vosk: {e}")
            return False

    def transcribe_audio(self, audio_data: bytes) -> Tuple[str, float]:
        """
        Transcribe audio data

        Args:
            audio_data: Audio bytes (PCM int16)

        Returns:
            Tuple of (transcribed_text, confidence)
        """
        if not self.is_initialized:
            logger.error("Vosk engine not initialized")
            return "", 0.0

        try:
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                text = result.get("result", [])
                text_str = " ".join([item.get("conf", "") for item in text])

                # Extract confidence from full result
                confidence = 0.9 if text else 0.0

            else:
                result = json.loads(self.recognizer.PartialResult())
                text_str = result.get("result", [])
                confidence = 0.0

            return text_str if text_str else "", confidence

        except Exception as e:
            logger.error(f"Error transcribing with Vosk: {e}")
            return "", 0.0

    def transcribe_stream(self, frames):
        """
        Transcribe audio stream (generator)

        Yields:
            Transcribed text chunks
        """
        if not self.is_initialized:
            logger.error("Vosk engine not initialized")
            return

        try:
            for data in frames:
                if isinstance(data, bytes):
                    self.recognizer.AcceptWaveform(data)
                    result = json.loads(self.recognizer.Result())

                    if "result" in result and result["result"]:
                        text = " ".join([item["conf"] for item in result["result"]])
                        yield text

        except Exception as e:
            logger.error(f"Error in stream transcription: {e}")

    def get_status(self) -> dict:
        """Get engine status"""
        return {
            "engine": "vosk",
            "initialized": self.is_initialized,
            "model_path": self.model_path,
            "sample_rate": self.sample_rate,
            "model_loaded": self.model is not None
        }

    @staticmethod
    def download_model(model_url: str = None):
        """Download Vosk model"""
        logger.info("To download Vosk models, visit: https://alphacephei.com/vosk/models")
        logger.info("Recommended: vosk-model-small-en (50MB)")
        logger.info("Alternative: vosk-model-en (1.4GB)")
        return True


# Global instance
_vosk_instance: Optional[VoskEngine] = None


def get_vosk_engine() -> VoskEngine:
    """Get or create Vosk engine instance"""
    global _vosk_instance
    if _vosk_instance is None:
        _vosk_instance = VoskEngine()
    return _vosk_instance
