"""Text-to-Speech API Routes"""

import base64
import numpy as np
from fastapi import APIRouter, HTTPException
from typing import Optional
from pathlib import Path
import tempfile

from src.api.schemas import SpeakRequest, SpeakResponse
from src.speech.synthesis.pyttsx3_engine import get_pyttsx3_engine
from src.ai.quota_manager import get_quota_manager
from src.audio.io import AudioFileIO
from src.config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/speak", response_model=SpeakResponse)
async def speak_text(request: SpeakRequest):
    """
    Convert text to speech

    Args:
        request: Speak request with text and voice settings
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")

        # Get TTS engine
        quota_manager = get_quota_manager()
        tts_backend = quota_manager.get_best_tts_backend()

        if tts_backend.value == "pyttsx3":
            tts_engine = get_pyttsx3_engine()

            if not tts_engine.is_initialized:
                raise HTTPException(status_code=503, detail="TTS engine not initialized")

            # Set voice if specified
            if request.voice and request.voice != "default":
                voices = tts_engine.list_voices()
                voice_found = False
                for i, voice in enumerate(voices):
                    if voice["name"].lower() == request.voice.lower():
                        tts_engine.set_voice(i)
                        voice_found = True
                        break

                if not voice_found:
                    logger.warning(f"Voice {request.voice} not found, using default")

            # Adjust speed
            rate = int(150 * request.speed)  # Default 150 WPM
            tts_engine.set_rate(rate)

            # Generate speech to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            success = tts_engine.speak_to_file(request.text, tmp_path)

            if not success:
                raise HTTPException(status_code=500, detail="Failed to generate speech")

            # Read audio file
            audio_data, sample_rate = AudioFileIO.read_audio_file(tmp_path)

            # Convert to base64
            audio_b64 = base64.b64encode(audio_data.tobytes()).decode("utf-8")

            # Calculate duration
            duration_seconds = len(audio_data) / sample_rate

            # Clean up
            Path(tmp_path).unlink()

            logger.info(f"Generated speech: {request.text[:50]}... ({duration_seconds:.1f}s)")

            return SpeakResponse(
                audio_data=audio_b64,
                duration_seconds=duration_seconds,
                voice_used=request.voice
            )

        else:
            raise HTTPException(status_code=503, detail="TTS backend not available")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@router.get("/voices")
async def list_voices():
    """List available voices"""
    try:
        tts_engine = get_pyttsx3_engine()

        if not tts_engine.is_initialized:
            raise HTTPException(status_code=503, detail="TTS engine not initialized")

        voices = tts_engine.list_voices()

        return {
            "voices": voices,
            "count": len(voices),
            "default_index": 0
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        raise HTTPException(status_code=500, detail="Could not list voices")


@router.get("/status")
async def get_tts_status():
    """Get text-to-speech engine status"""
    try:
        tts_engine = get_pyttsx3_engine()
        quota_manager = get_quota_manager()

        return {
            "pyttsx3_status": tts_engine.get_status(),
            "current_backend": quota_manager.current_backends["tts"].value,
            "backends_available": ["pyttsx3", "azure"]
        }

    except Exception as e:
        logger.error(f"Error getting TTS status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/preview")
async def preview_voice(voice: str = "default", text: str = "Hello, this is a voice preview"):
    """Get audio preview of a voice"""
    try:
        if not text:
            text = "Hello, this is a voice preview"

        if len(text) > 200:
            text = text[:200]  # Limit preview length

        # Use speak endpoint logic
        request = SpeakRequest(text=text, voice=voice, speed=1.0)
        return await speak_text(request)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error preview voice: {e}")
        raise HTTPException(status_code=500, detail="Could not preview voice")
