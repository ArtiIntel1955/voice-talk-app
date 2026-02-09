"""Audio File I/O Module - Read and Write Audio Files"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple
import subprocess

from ..config.logger import get_logger

logger = get_logger(__name__)


class AudioFileIO:
    """Handle reading and writing audio files"""

    SUPPORTED_FORMATS = ("wav", "flac", "ogg", "mp3", "m4a")

    @staticmethod
    def read_audio_file(file_path: str) -> Tuple[np.ndarray, int]:
        """
        Read audio file

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")

            # Try soundfile first (works with WAV, FLAC, OGG)
            if file_path.suffix.lower() in [".wav", ".flac", ".ogg"]:
                audio_data, sample_rate = sf.read(str(file_path), dtype=np.int16)
                logger.info(f"Loaded audio file: {file_path} ({sample_rate}Hz)")
                return audio_data, sample_rate

            # For MP3, use pydub or ffmpeg
            else:
                return AudioFileIO._read_with_pydub(file_path)

        except Exception as e:
            logger.error(f"Error reading audio file {file_path}: {e}")
            raise

    @staticmethod
    def _read_with_pydub(file_path: Path) -> Tuple[np.ndarray, int]:
        """Read audio file using pydub"""
        try:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(str(file_path))

            # Convert to numpy array
            audio_array = np.array(audio.get_array_of_samples())

            # Handle stereo -> mono if needed
            if audio.channels == 2:
                audio_array = audio_array.reshape((-1, 2))
                audio_array = audio_array.mean(axis=1)

            logger.info(f"Loaded audio file via pydub: {file_path} ({audio.frame_rate}Hz)")
            return audio_array.astype(np.int16), audio.frame_rate

        except Exception as e:
            logger.error(f"Failed to read with pydub: {e}")
            raise

    @staticmethod
    def write_audio_file(
        file_path: str,
        audio_data: np.ndarray,
        sample_rate: int,
        format: str = "wav"
    ) -> bool:
        """
        Write audio to file

        Args:
            file_path: Output file path
            audio_data: Audio data as numpy array
            sample_rate: Sample rate in Hz
            format: Output format (wav, flac, ogg, mp3)
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Use soundfile for supported formats
            if format.lower() in ["wav", "flac", "ogg"]:
                sf.write(str(file_path), audio_data, sample_rate, subtype='PCM_16')
                logger.info(f"Wrote audio file: {file_path}")
                return True

            # Use pydub for MP3
            elif format.lower() == "mp3":
                return AudioFileIO._write_with_pydub(file_path, audio_data, sample_rate, "mp3")

            else:
                logger.error(f"Unsupported format: {format}")
                return False

        except Exception as e:
            logger.error(f"Error writing audio file {file_path}: {e}")
            return False

    @staticmethod
    def _write_with_pydub(file_path: Path, audio_data: np.ndarray, sample_rate: int, format: str) -> bool:
        """Write audio using pydub"""
        try:
            from pydub

            # Create AudioSegment
            audio = AudioSegment(
                audio_data.tobytes(),
                frame_rate=sample_rate,
                sample_width=audio_data.dtype.itemsize,
                channels=1
            )

            # Export
            audio.export(str(file_path), format=format)
            logger.info(f"Wrote audio file via pydub: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to write with pydub: {e}")
            return False

    @staticmethod
    def convert_audio_format(
        input_path: str,
        output_path: str,
        target_format: str,
        target_sample_rate: Optional[int] = None
    ) -> bool:
        """
        Convert audio file to different format

        Args:
            input_path: Input file path
            output_path: Output file path
            target_format: Output format (wav, mp3, flac, ogg)
            target_sample_rate: Target sample rate (optional)
        """
        try:
            audio_data, sample_rate = AudioFileIO.read_audio_file(input_path)

            # Resample if needed
            if target_sample_rate and target_sample_rate != sample_rate:
                from .processor import AudioProcessor
                audio_data = AudioProcessor.resample_audio(audio_data, sample_rate, target_sample_rate)
                sample_rate = target_sample_rate

            return AudioFileIO.write_audio_file(output_path, audio_data, sample_rate, target_format)

        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return False

    @staticmethod
    def get_audio_info(file_path: str) -> Optional[dict]:
        """Get metadata about audio file"""
        try:
            file_path = Path(file_path)

            # Try soundfile first
            if file_path.suffix.lower() in [".wav", ".flac", ".ogg"]:
                info = sf.info(str(file_path))
                return {
                    "duration": info.duration,
                    "sample_rate": info.samplerate,
                    "channels": info.channels,
                    "format": info.format,
                    "subtype": info.subtype
                }

            # Try pydub for other formats
            else:
                from pydub
                audio = AudioSegment.from_file(str(file_path))
                return {
                    "duration": len(audio) / 1000.0,  # Convert to seconds
                    "sample_rate": audio.frame_rate,
                    "channels": audio.channels,
                    "format": file_path.suffix.lower(),
                    "frame_width": audio.frame_width
                }

        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return None
