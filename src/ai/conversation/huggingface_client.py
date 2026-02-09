"""Hugging Face API Integration for Conversational AI"""

import requests
from typing import Optional, Tuple
from datetime import datetime, timedelta
import json

from ..config.settings import get_settings
from ..config.logger import get_logger
from ..database.database import init_sync_db
from ..database.models import APIQuotaTracker

logger = get_logger(__name__)


class HuggingFaceClient:
    """Hugging Face API client for conversational AI"""

    API_BASE_URL = "https://api-inference.huggingface.co/models"

    def __init__(self):
        """Initialize Hugging Face client"""
        settings = get_settings()
        self.ai_settings = settings.conversational_ai

        self.api_key = self.ai_settings.huggingface_api_key
        self.model_id = self.ai_settings.huggingface_model_id
        self.is_initialized = bool(self.api_key)
        self.timeout = settings.speech_recognition.timeout_seconds

        if not self.is_initialized:
            logger.warning("Hugging Face API key not set")

    def chat(self, message: str, session_context: Optional[list] = None) -> Tuple[str, bool]:
        """
        Send message to conversational AI

        Args:
            message: User message
            session_context: Conversation history for context

        Returns:
            Tuple of (response_text, success)
        """
        if not self.is_initialized:
            logger.error("Hugging Face API not initialized (no API key)")
            return "", False

        try:
            # Check quota first
            if not self._check_quota("huggingface"):
                logger.warning("Hugging Face quota exceeded, fallback to offline mode")
                return "", False

            # Prepare prompt with context
            prompt = self._prepare_prompt(message, session_context)

            # Call API
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 256,
                    "temperature": 0.7,
                }
            }

            response = requests.post(
                f"{self.API_BASE_URL}/{self.model_id}",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()

                # Extract text from response
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and "generated_text" in result[0]:
                        generated_text = result[0]["generated_text"]
                        response_text = self._extract_response(generated_text, prompt)

                        # Track usage
                        self._track_quota("huggingface")

                        logger.debug(f"HuggingFace response: {response_text[:100]}...")
                        return response_text, True

                logger.error(f"Unexpected response format: {result}")
                return "", False

            elif response.status_code == 429:  # Rate limited
                logger.warning("Hugging Face API rate limited")
                return "", False

            else:
                logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                return "", False

        except Exception as e:
            logger.error(f"Error calling Hugging Face API: {e}")
            return "", False

    def _prepare_prompt(self, message: str, context: Optional[list] = None) -> str:
        """Prepare prompt with context"""
        prompt = message

        if context:
            # Add conversation history as context
            for msg in context[-5:]:  # Last 5 messages for context
                if msg.get("role") == "user":
                    prompt = f"User: {msg.get('content', '')}\n{prompt}"

        return prompt

    def _extract_response(self, generated_text: str, prompt: str) -> str:
        """Extract response from generated text"""
        # Remove prompt from generated text
        if generated_text.startswith(prompt):
            return generated_text[len(prompt):].strip()
        return generated_text.strip()

    def _check_quota(self, service_name: str) -> bool:
        """Check if quota is available"""
        try:
            engine, session_local = init_sync_db()
            session = session_local()

            # Get quota tracker
            tracker = session.query(APIQuotaTracker).filter_by(service_name=service_name).first()

            if not tracker:
                # Create new tracker
                tracker = APIQuotaTracker(
                    service_name=service_name,
                    daily_calls=0,
                    daily_limit=1000  # Default limit
                )
                session.add(tracker)
                session.commit()

            # Reset if new day
            if (datetime.now() - tracker.last_reset_date).days > 0:
                tracker.daily_calls = 0
                tracker.last_reset_date = datetime.now()

            # Check if under limit
            return tracker.daily_calls < tracker.daily_limit

        except Exception as e:
            logger.error(f"Error checking quota: {e}")
            return True  # Allow by default

        finally:
            session.close()

    def _track_quota(self, service_name: str):
        """Track API usage"""
        try:
            engine, session_local = init_sync_db()
            session = session_local()

            tracker = session.query(APIQuotaTracker).filter_by(service_name=service_name).first()

            if tracker:
                tracker.daily_calls += 1
                tracker.is_quota_exceeded = tracker.daily_calls >= tracker.daily_limit
                tracker.updated_at = datetime.now()
                session.commit()

                logger.debug(f"Quota tracked: {tracker.daily_calls}/{tracker.daily_limit}")

        except Exception as e:
            logger.error(f"Error tracking quota: {e}")

        finally:
            session.close()

    def get_status(self) -> dict:
        """Get API status"""
        return {
            "engine": "huggingface",
            "initialized": self.is_initialized,
            "model_id": self.model_id,
            "has_api_key": bool(self.api_key)
        }


# Global instance
_hf_instance: Optional[HuggingFaceClient] = None


def get_huggingface_client() -> HuggingFaceClient:
    """Get or create Hugging Face client"""
    global _hf_instance
    if _hf_instance is None:
        _hf_instance = HuggingFaceClient()
    return _hf_instance
