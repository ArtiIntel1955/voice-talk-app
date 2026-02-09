"""Audio Playback Module - Audio Output to Speakers"""

import numpy as np
import pyaudio
from typing import Optional, List
import threading
import time

from ..config.settings import get_settings
from ..config.logger import get_logger

logger = get_logger(__name__)


class AudioPlayback:
    """Handles audio playback to speaker"""

    def __init__(self):
        """Initialize audio playback"""
        settings = get_settings()
        self.audio_settings = settings.audio

        self.sample_rate = self.audio_settings.sample_rate
        self.channels = self.audio_settings.channels
        self.chunk_size = self.audio_settings.chunk_size
        self.device_index = self.audio_settings.device_index

        self.audio = None
        self.stream = None
        self.is_playing = False

        logger.info(f"AudioPlayback initialized: {self.sample_rate}Hz, {self.channels}ch")

    def list_output_devices(self) -> List[dict]:
        """List available audio output devices"""
        audio = pyaudio.PyAudio()
        devices = []

        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxOutputChannels'] > 0:  # Only output devices
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxOutputChannels'],
                    'sample_rate': int(info['defaultSampleRate']),
                    'default': info['index'] == audio.get_default_output_device_info()['index']
                })

        audio.terminate()
        logger.info(f"Found {len(devices)} audio output devices")
        return devices

    def start(self) -> bool:
        """Initialize audio playback stream"""
        try:
            self.audio = pyaudio.PyAudio()

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )

            self.is_playing = True
            logger.info("Audio playback stream opened")
            return True

        except Exception as e:
            logger.error(f"Failed to start audio playback: {e}")
            if self.audio:
                self.audio.terminate()
            return False

    def stop(self):
        """Stop audio playback"""
        self.is_playing = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            logger.info("Audio playback stream closed")

        if self.audio:
            self.audio.terminate()
            logger.info("PyAudio terminated")

    def play_audio(self, audio_data: np.ndarray, blocking: bool = True) -> bool:
        """
        Play audio data

        Args:
            audio_data: Audio data as numpy array (int16)
            blocking: If True, wait for playback to complete
        """
        if not self.is_playing or not self.stream:
            logger.warning("Audio playback not ready")
            return False

        try:
            # Convert to bytes if needed
            if isinstance(audio_data, np.ndarray):
                audio_bytes = audio_data.astype(np.int16).tobytes()
            else:
                audio_bytes = audio_data

            # Write to stream
            self.stream.write(audio_bytes)

            if blocking:
                # Wait for playback to complete
                duration_seconds = len(audio_data) / self.sample_rate
                time.sleep(duration_seconds)

            logger.debug(f"Played {len(audio_data)} audio samples")
            return True

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False

    def play_audio_async(self, audio_data: np.ndarray) -> threading.Thread:
        """Play audio in a background thread"""
        thread = threading.Thread(target=self.play_audio, args=(audio_data, True))
        thread.daemon = True
        thread.start()
        return thread

    def get_device_index(self) -> Optional[int]:
        """Get current output device index"""
        return self.device_index

    def set_device_index(self, device_index: int):
        """Set output device index (requires restart)"""
        self.device_index = device_index
        was_playing = self.is_playing
        if was_playing:
            self.stop()
        self.start()
        logger.info(f"Audio output device changed to index {device_index}")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def __del__(self):
        """Cleanup on deletion"""
        if self.is_playing:
            self.stop()
