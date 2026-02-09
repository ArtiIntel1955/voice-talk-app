"""Speech Recognition API Routes"""

import base64
import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional

from ..api.schemas import TranscribeRequest, TranscribeResponse
from ..speech.recognition.vosk_engine import get_vosk_engine
from ..ai.quota_manager import get_quota_manager
from ..config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio to text

    Args:
        request: Transcribe request with base64 audio data
    """
    try:
        # Decode audio data
        audio_bytes = base64.b64decode(request.audio_data)

        # Get appropriate STT engine
        quota_manager = get_quota_manager()
        stt_backend = quota_manager.get_best_stt_backend()

        if stt_backend.value == "vosk":
            vosk_engine = get_vosk_engine()

            if not vosk_engine.is_initialized:
                raise HTTPException(
                    status_code=503,
                    detail="Vosk engine not initialized. Download model from https://alphacephei.com/vosk/models"
                )

            # Transcribe
            text, confidence = vosk_engine.transcribe_audio(audio_bytes)

            # Calculate duration
            duration_seconds = len(audio_bytes) / (request.sample_rate * 2)  # 16-bit = 2 bytes

            logger.info(f"Transcribed audio: {text[:50]}...")

            return TranscribeResponse(
                text=text,
                confidence=confidence,
                duration_seconds=duration_seconds
            )

        else:
            raise HTTPException(status_code=503, detail="STT backend not available")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


@router.post("/status")
async def get_stt_status():
    """Get speech recognition engine status"""
    try:
        vosk_engine = get_vosk_engine()
        quota_manager = get_quota_manager()

        return {
            "vosk_status": vosk_engine.get_status(),
            "current_backend": quota_manager.current_backends["stt"].value,
            "backends_available": ["vosk", "huggingface"]
        }

    except Exception as e:
        logger.error(f"Error getting STT status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/devices")
async def list_audio_devices():
    """List available audio input devices"""
    try:
        from ..audio.capture import AudioCapture

        capture = AudioCapture()
        devices = capture.list_devices()

        return {
            "devices": devices,
            "count": len(devices)
        }

    except Exception as e:
        logger.error(f"Error listing audio devices: {e}")
        raise HTTPException(status_code=500, detail="Could not list devices")
