"""Smart Model Switching and Quota Management System"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from enum import Enum

from ..config.logger import get_logger
from ..database.database import init_sync_db
from ..database.models import APIQuotaTracker

logger = get_logger(__name__)


class AIBackend(Enum):
    """Available AI backends"""
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    FALLBACK = "fallback"  # Fixed response


class STTBackend(Enum):
    """Available STT backends"""
    VOSK = "vosk"
    SHERPA_ONNX = "sherpa-onnx"
    HUGGINGFACE = "huggingface"


class TTSBackend(Enum):
    """Available TTS backends"""
    PYTTSX3 = "pyttsx3"
    AZURE = "azure"
    ESPEAK = "espeak"


class QuotaManager:
    """Manages API quotas and smart model switching"""

    # Default quota limits
    DEFAULT_QUOTAS = {
        "huggingface": 1000,  # Daily calls
        "azure_tts": 5000000,  # Characters per month
        "vosk": float("inf"),  # Unlimited (local)
        "ollama": float("inf"),  # Unlimited (local)
    }

    def __init__(self):
        """Initialize quota manager"""
        self.current_backends = {
            "ai": AIBackend.HUGGINGFACE,
            "stt": STTBackend.VOSK,
            "tts": TTSBackend.PYTTSX3
        }
        self._initialize_quota_trackers()

    def _initialize_quota_trackers(self):
        """Initialize quota trackers in database"""
        try:
            engine, session_local = init_sync_db()
            session = session_local()

            for service, limit in self.DEFAULT_QUOTAS.items():
                tracker = session.query(APIQuotaTracker).filter_by(service_name=service).first()

                if not tracker:
                    tracker = APIQuotaTracker(
                        service_name=service,
                        daily_calls=0,
                        daily_limit=int(limit) if limit != float("inf") else 999999
                    )
                    session.add(tracker)

            session.commit()
            logger.info("Quota trackers initialized")

        except Exception as e:
            logger.error(f"Error initializing quota trackers: {e}")

        finally:
            session.close()

    def check_quota(self, service_name: str) -> Tuple[bool, int]:
        """
        Check if quota is available

        Returns:
            Tuple of (quota_available, calls_remaining)
        """
        try:
            engine, session_local = init_sync_db()
            session = session_local()

            tracker = session.query(APIQuotaTracker).filter_by(service_name=service_name).first()

            if not tracker:
                # Assume unlimited if not tracked
                return True, 999999

            # Reset if new day
            if (datetime.now() - tracker.last_reset_date).days >= 1:
                tracker.daily_calls = 0
                tracker.last_reset_date = datetime.now()
                session.commit()

            calls_remaining = max(0, tracker.daily_limit - tracker.daily_calls)
            quota_ok = tracker.daily_calls < tracker.daily_limit

            logger.debug(f"{service_name} quota: {tracker.daily_calls}/{tracker.daily_limit}")
            return quota_ok, calls_remaining

        except Exception as e:
            logger.error(f"Error checking quota for {service_name}: {e}")
            return True, 999999

        finally:
            session.close()

    def track_usage(self, service_name: str, units: int = 1):
        """Track API usage"""
        try:
            engine, session_local = init_sync_db()
            session = session_local()

            tracker = session.query(APIQuotaTracker).filter_by(service_name=service_name).first()

            if tracker:
                tracker.daily_calls += units
                tracker.updated_at = datetime.now()

                # Check if exceeded
                tracker.is_quota_exceeded = tracker.daily_calls >= tracker.daily_limit

                session.commit()
                logger.debug(f"Usage tracked for {service_name}: {units} units")

        except Exception as e:
            logger.error(f"Error tracking usage for {service_name}: {e}")

        finally:
            session.close()

    def get_best_ai_backend(self) -> AIBackend:
        """
        Determine best AI backend based on quota availability

        Priority: HuggingFace > Ollama > Fallback
        """
        # Check HuggingFace quota
        hf_ok, hf_remaining = self.check_quota("huggingface")

        if hf_ok and hf_remaining > 0:
            logger.debug("Using HuggingFace for AI")
            self.current_backends["ai"] = AIBackend.HUGGINGFACE
            return AIBackend.HUGGINGFACE

        # Try Ollama as fallback
        logger.info("HuggingFace quota exceeded or unavailable, trying Ollama")
        self.current_backends["ai"] = AIBackend.OLLAMA
        return AIBackend.OLLAMA

    def get_best_stt_backend(self, require_online: bool = False) -> STTBackend:
        """
        Determine best STT backend

        Priority: Vosk (offline) > HuggingFace (online) > Fallback
        """
        if not require_online:
            # Prefer offline Vosk
            logger.debug("Using Vosk for STT (offline)")
            self.current_backends["stt"] = STTBackend.VOSK
            return STTBackend.VOSK

        # Online required
        hf_ok, _ = self.check_quota("huggingface")

        if hf_ok:
            logger.debug("Using HuggingFace for STT (online)")
            self.current_backends["stt"] = STTBackend.HUGGINGFACE
            return STTBackend.HUGGINGFACE

        # Fallback to offline
        logger.warning("HuggingFace quota exceeded, falling back to Vosk")
        self.current_backends["stt"] = STTBackend.VOSK
        return STTBackend.VOSK

    def get_best_tts_backend(self) -> TTSBackend:
        """
        Determine best TTS backend based on quota

        Priority: Pyttsx3 (offline) > Azure (cloud) > Fallback
        """
        # Prefer offline Pyttsx3
        logger.debug("Using Pyttsx3 for TTS (offline)")
        self.current_backends["tts"] = TTSBackend.PYTTSX3
        return TTSBackend.PYTTSX3

    def get_quota_status(self) -> Dict:
        """Get overall quota status"""
        status = {}

        for service in self.DEFAULT_QUOTAS.keys():
            ok, remaining = self.check_quota(service)
            status[service] = {
                "available": ok,
                "calls_remaining": remaining,
                "current_backend": self.current_backends.get("ai") if "ai" in service else None
            }

        return status

    def get_backend_status(self) -> Dict:
        """Get current backend selection status"""
        return {
            "ai_backend": self.current_backends["ai"].value,
            "stt_backend": self.current_backends["stt"].value,
            "tts_backend": self.current_backends["tts"].value
        }

    def should_switch_backend(self, service_type: str) -> bool:
        """Check if should switch to different backend"""
        if service_type == "ai":
            best = self.get_best_ai_backend()
            return best != self.current_backends["ai"]

        elif service_type == "stt":
            best = self.get_best_stt_backend()
            return best != self.current_backends["stt"]

        elif service_type == "tts":
            best = self.get_best_tts_backend()
            return best != self.current_backends["tts"]

        return False


# Global instance
_quota_manager: Optional[QuotaManager] = None


def get_quota_manager() -> QuotaManager:
    """Get or create quota manager instance"""
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager()
    return _quota_manager
