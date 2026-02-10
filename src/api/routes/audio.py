"""Audio File Processing API Routes"""

import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
import os

from src.audio.io import AudioFileIO
from src.speech.recognition.vosk_engine import get_vosk_engine
from src.config.logger import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

router = APIRouter(prefix="/audio", tags=["audio"])

# Store uploaded files
UPLOAD_DIR = Path("./data/audio_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file for processing

    Args:
        file: Audio file (WAV, MP3, FLAC, OGG, M4A)

    Returns:
        File ID and metadata
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Check file extension
        valid_extensions = (".wav", ".mp3", ".flac", ".ogg", ".m4a")
        if not file.filename.lower().endswith(valid_extensions):
            raise HTTPException(status_code=400, detail=f"Invalid file format. Supported: {valid_extensions}")

        # Generate file ID
        file_id = str(uuid.uuid4())[:8]

        # Save file
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Get audio info
        audio_info = AudioFileIO.get_audio_info(str(file_path))

        if not audio_info:
            raise HTTPException(status_code=400, detail="Could not read audio file")

        logger.info(f"Uploaded audio file: {file_id} ({audio_info['duration']}s)")

        return {
            "file_id": file_id,
            "filename": file.filename,
            "size_bytes": len(content),
            "duration_seconds": audio_info["duration"],
            "sample_rate": audio_info["sample_rate"],
            "channels": audio_info["channels"],
            "format": audio_info["format"]
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error uploading audio: {e}")
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@router.post("/transcribe/{file_id}")
async def transcribe_audio_file(file_id: str, language: str = "en-US"):
    """
    Transcribe an uploaded audio file

    Args:
        file_id: File ID from upload
        language: Language code

    Returns:
        Transcribed text
    """
    try:
        # Find file
        file_path = None
        for f in UPLOAD_DIR.glob(f"{file_id}_*"):
            file_path = f
            break

        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")

        # Read audio
        audio_data, sample_rate = AudioFileIO.read_audio_file(str(file_path))

        # Get Vosk engine
        vosk_engine = get_vosk_engine()

        if not vosk_engine.is_initialized:
            raise HTTPException(status_code=503, detail="STT engine not initialized")

        # Transcribe in chunks
        from ..audio.processor import AudioProcessor

        chunks = AudioProcessor.split_audio_chunks(audio_data, sample_rate, chunk_duration_ms=5000)
        all_text = []

        for chunk in chunks:
            chunk_bytes = chunk.astype('int16').tobytes()
            text, confidence = vosk_engine.transcribe_audio(chunk_bytes)
            if text:
                all_text.append(text)

        transcribed_text = " ".join(all_text)
        duration_seconds = len(audio_data) / sample_rate

        logger.info(f"Transcribed file {file_id}: {len(transcribed_text)} chars, {duration_seconds:.1f}s")

        return {
            "file_id": file_id,
            "text": transcribed_text,
            "word_count": len(transcribed_text.split()),
            "duration_seconds": duration_seconds,
            "language": language
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error transcribing file: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


@router.post("/convert/{file_id}")
async def convert_audio_format(file_id: str, target_format: str = "wav", target_sample_rate: int = None):
    """
    Convert audio file to different format

    Args:
        file_id: File ID from upload
        target_format: Target format (wav, mp3, flac, ogg)
        target_sample_rate: Target sample rate (optional)

    Returns:
        Converted file path
    """
    try:
        # Find file
        file_path = None
        for f in UPLOAD_DIR.glob(f"{file_id}_*"):
            file_path = f
            break

        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")

        # Validate target format
        valid_formats = ("wav", "mp3", "flac", "ogg")
        if target_format.lower() not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Invalid format: {target_format}")

        # Convert
        output_path = UPLOAD_DIR / f"{file_id}_converted.{target_format}"

        success = AudioFileIO.convert_audio_format(
            str(file_path),
            str(output_path),
            target_format.lower(),
            target_sample_rate
        )

        if not success:
            raise HTTPException(status_code=500, detail="Conversion failed")

        logger.info(f"Converted file {file_id} to {target_format}")

        return {
            "file_id": file_id,
            "original_format": file_path.suffix,
            "target_format": target_format,
            "output_filename": output_path.name,
            "status": "success"
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@router.get("/info/{file_id}")
async def get_audio_info(file_id: str):
    """Get information about an uploaded file"""
    try:
        # Find file
        file_path = None
        for f in UPLOAD_DIR.glob(f"{file_id}_*"):
            file_path = f
            break

        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")

        # Get info
        audio_info = AudioFileIO.get_audio_info(str(file_path))

        if not audio_info:
            raise HTTPException(status_code=400, detail="Could not read audio file")

        return {
            "file_id": file_id,
            "filename": file_path.name,
            "size_bytes": file_path.stat().st_size,
            **audio_info
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting audio info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/delete/{file_id}")
async def delete_audio_file(file_id: str):
    """Delete an uploaded audio file"""
    try:
        # Find file
        file_path = None
        for f in UPLOAD_DIR.glob(f"{file_id}_*"):
            file_path = f
            break

        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")

        # Delete file
        file_path.unlink()

        logger.info(f"Deleted audio file: {file_id}")

        return {
            "file_id": file_id,
            "status": "deleted"
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
