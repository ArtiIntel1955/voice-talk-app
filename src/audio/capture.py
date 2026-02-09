"""Audio Capture Module - Real-time Audio Input"""

import numpy as np
import pyaudio
import threading
from typing import Optional, Callable, List
from queue import Queue
from dataclasses import dataclass

from ..config.settings import get_settings
from ..config.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AudioFrame:
    """Represents a single audio frame"""
    data: np.ndarray
    sample_rate: int
    timestamp: float
    duration_seconds: float


class AudioCapture:
    """Handles real-time audio capture from microphone"""

    def __init__(self):
        """Initialize audio capture"""
        settings = get_settings()
        self.audio_settings = settings.audio

        self.sample_rate = self.audio_settings.sample_rate
        self.channels = self.audio_settings.channels
        self.chunk_size = self.audio_settings.chunk_size
        self.device_index = self.audio_settings.device_index

        self.audio = None
        self.stream = None
        self.is_recording = False
        self.audio_queue: Queue[AudioFrame] = Queue()

        # Callbacks
        self.on_frame_callback: Optional[Callable[[AudioFrame], None]] = None

        logger.info(f"AudioCapture initialized: {self.sample_rate}Hz, {self.channels}ch, {self.chunk_size}B chunks")

    def list_devices(self) -> List[dict]:
        """List available audio input devices"""
        audio = pyaudio.PyAudio()
        devices = []

        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Only input devices
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'channels': info['maxInputChannels'],
                    'sample_rate': int(info['defaultSampleRate']),
                    'default': info['index'] == audio.get_default_input_device_info()['index']
                })

        audio.terminate()
        logger.info(f"Found {len(devices)} audio input devices")
        return devices

    def start(self) -> bool:
        """Start recording audio"""
        try:
            self.audio = pyaudio.PyAudio()

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback if self.on_frame_callback else None,
                start=False
            )

            self.is_recording = True

            # Start stream
            if self.stream:
                self.stream.start_stream()
                logger.info("Audio capture started")
                return True

        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            if self.audio:
                self.audio.terminate()
            return False

    def stop(self):
        """Stop recording audio"""
        self.is_recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            logger.info("Audio stream stopped")

        if self.audio:
            self.audio.terminate()
            logger.info("PyAudio terminated")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Internal callback for streaming audio"""
        if status:
            logger.warning(f"Audio stream status: {status}")

        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)

        # Create frame
        frame = AudioFrame(
            data=audio_data,
            sample_rate=self.sample_rate,
            timestamp=time_info.input_buffer_adc_time,
            duration_seconds=len(audio_data) / self.sample_rate
        )

        # Add to queue
        self.audio_queue.put(frame)

        # Call callback if provided
        if self.on_frame_callback:
            self.on_frame_callback(frame)

        return (in_data, pyaudio.paContinue)

    def read_frame(self) -> Optional[AudioFrame]:
        """Read a single audio frame (blocking)"""
        if not self.is_recording or not self.stream:
            return None

        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.int16)

            frame = AudioFrame(
                data=audio_array,
                sample_rate=self.sample_rate,
                timestamp=0.0,  # Would need to track this properly
                duration_seconds=len(audio_array) / self.sample_rate
            )

            return frame

        except Exception as e:
            logger.error(f"Error reading audio frame: {e}")
            return None

    def read_frames_buffered(self, timeout: float = 1.0) -> Optional[AudioFrame]:
        """Read audio frame from queue (non-blocking with timeout)"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except:
            return None

    def get_device_index(self) -> Optional[int]:
        """Get current device index"""
        return self.device_index

    def set_device_index(self, device_index: int):
        """Set device index (requires restart)"""
        self.device_index = device_index
        was_recording = self.is_recording
        if was_recording:
            self.stop()
        self.start()
        logger.info(f"Audio device changed to index {device_index}")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def __del__(self):
        """Cleanup on deletion"""
        if self.is_recording:
            self.stop()
