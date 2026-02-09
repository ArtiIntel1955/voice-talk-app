"""Audio Processing Module - Audio Enhancement and Processing"""

import numpy as np
import librosa
from typing import Tuple, Optional
import warnings

from ..config.logger import get_logger

logger = get_logger(__name__)

# Suppress librosa warnings
warnings.filterwarnings('ignore', category=UserWarning)


class AudioProcessor:
    """Process and enhance audio data"""

    @staticmethod
    def normalize_audio(audio_data: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normalize audio to target loudness level

        Args:
            audio_data: Audio array
            target_db: Target decibel level
        """
        try:
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            if rms == 0:
                return audio_data

            # Calculate current dB level
            current_db = 20 * np.log10(rms / 32767.0)
            gain = 10 ** ((target_db - current_db) / 20.0)

            # Apply gain with clipping
            normalized = np.clip(audio_data.astype(np.float32) * gain, -32768, 32767)
            return normalized.astype(np.int16)

        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            return audio_data

    @staticmethod
    def remove_silence(audio_data: np.ndarray, sample_rate: int, threshold_db: float = -40.0) -> np.ndarray:
        """
        Remove silence from audio

        Args:
            audio_data: Audio array
            sample_rate: Sample rate in Hz
            threshold_db: Silence threshold in dB
        """
        try:
            # Convert to float
            audio_float = audio_data.astype(np.float32) / 32768.0

            # Use librosa for silence detection
            S = librosa.feature.melspectrogram(y=audio_float, sr=sample_rate)
            S_db = librosa.power_to_db(S)

            # Simple energy-based silence detection
            energy = np.sqrt(np.mean(audio_float ** 2))
            energy_db = 20 * np.log10(energy) if energy > 0 else -np.inf

            if energy_db < threshold_db:
                logger.debug("Audio is mostly silence")
                return np.array([], dtype=np.int16)

            return audio_data

        except Exception as e:
            logger.error(f"Error removing silence: {e}")
            return audio_data

    @staticmethod
    def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """
        Resample audio to target sample rate

        Args:
            audio_data: Audio array
            orig_sr: Original sample rate
            target_sr: Target sample rate
        """
        try:
            if orig_sr == target_sr:
                return audio_data

            audio_float = audio_data.astype(np.float32) / 32768.0
            resampled = librosa.resample(audio_float, orig_sr=orig_sr, target_sr=target_sr)
            resampled = np.clip(resampled * 32767.0, -32768, 32767)

            logger.debug(f"Resampled audio from {orig_sr}Hz to {target_sr}Hz")
            return resampled.astype(np.int16)

        except Exception as e:
            logger.error(f"Error resampling audio: {e}")
            return audio_data

    @staticmethod
    def detect_voice_activity(audio_data: np.ndarray, sample_rate: int) -> Tuple[bool, float]:
        """
        Detect voice activity in audio

        Args:
            audio_data: Audio array
            sample_rate: Sample rate in Hz

        Returns:
            Tuple of (has_voice, confidence)
        """
        try:
            audio_float = audio_data.astype(np.float32) / 32768.0

            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio_float ** 2))

            # Simple threshold-based VAD
            # Voice typically has RMS > 0.02
            has_voice = rms > 0.01
            confidence = min(rms / 0.1, 1.0)  # Normalize to 0-1

            return has_voice, float(confidence)

        except Exception as e:
            logger.error(f"Error detecting voice activity: {e}")
            return False, 0.0

    @staticmethod
    def split_audio_chunks(audio_data: np.ndarray, sample_rate: int, chunk_duration_ms: int = 5000) -> list:
        """
        Split audio into chunks

        Args:
            audio_data: Audio array
            sample_rate: Sample rate in Hz
            chunk_duration_ms: Duration of each chunk in milliseconds
        """
        chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        chunks = []

        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            if len(chunk) > 0:
                chunks.append(chunk)

        logger.debug(f"Split audio into {len(chunks)} chunks of {chunk_duration_ms}ms")
        return chunks

    @staticmethod
    def concatenate_chunks(chunks: list) -> np.ndarray:
        """Concatenate audio chunks into single array"""
        if not chunks:
            return np.array([], dtype=np.int16)
        return np.concatenate(chunks, axis=0)

    @staticmethod
    def apply_gain(audio_data: np.ndarray, gain_db: float) -> np.ndarray:
        """
        Apply gain to audio

        Args:
            audio_data: Audio array
            gain_db: Gain in decibels
        """
        try:
            gain_linear = 10 ** (gain_db / 20.0)
            amplified = np.clip(audio_data.astype(np.float32) * gain_linear, -32768, 32767)
            return amplified.astype(np.int16)
        except Exception as e:
            logger.error(f"Error applying gain: {e}")
            return audio_data

    @staticmethod
    def get_audio_duration(audio_data: np.ndarray, sample_rate: int) -> float:
        """Get duration of audio in seconds"""
        return len(audio_data) / sample_rate

    @staticmethod
    def get_rms_energy(audio_data: np.ndarray) -> float:
        """Get RMS (root mean square) energy of audio"""
        audio_float = audio_data.astype(np.float32) / 32768.0
        return float(np.sqrt(np.mean(audio_float ** 2)))

    @staticmethod
    def estimate_loudness_db(audio_data: np.ndarray) -> float:
        """Estimate loudness in decibels"""
        rms = AudioProcessor.get_rms_energy(audio_data)
        if rms == 0:
            return -np.inf
        return 20 * np.log10(rms)
