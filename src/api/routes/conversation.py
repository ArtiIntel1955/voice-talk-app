"""Conversation API Routes"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime

from ..api.schemas import ChatRequest, ChatResponse, Message, ErrorResponse
from ..ai.conversation.huggingface_client import get_huggingface_client
from ..ai.quota_manager import get_quota_manager
from ..database.database import get_async_db
from ..database.models import ConversationSession, Message as MessageModel
from ..config.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversation"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get AI response

    Args:
        request: Chat request with message and optional session ID
    """
    try:
        # Get or create session
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
            logger.info(f"Created new conversation session: {request.session_id}")

        # Validate message
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if len(request.message) > 5000:
            raise HTTPException(status_code=400, detail="Message too long (max 5000 characters)")

        # Get quota manager and determine which backend to use
        quota_manager = get_quota_manager()
        best_backend = quota_manager.get_best_ai_backend()

        # Get conversation context if requested
        context = []
        if request.include_context:
            # In a real app, we'd load from database
            context = []

        # Get HuggingFace client
        hf_client = get_huggingface_client()

        # Send message to AI
        response_text, success = hf_client.chat(request.message, context)

        if not success or not response_text:
            logger.warning("Failed to get AI response, returning fallback")
            response_text = "I'm having trouble understanding that right now. Please try again."
            backend_used = "fallback"

        else:
            backend_used = best_backend.value
            quota_manager.track_usage("huggingface")

        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            tokens_used=None,  # Would be tracked by API
            backend_used=backend_used
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/history/{session_id}")
async def get_conversation_history(session_id: str):
    """
    Get conversation history for a session

    Args:
        session_id: Session identifier
    """
    try:
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")

        # In a real app, load from database
        history = {
            "session_id": session_id,
            "messages": [],
            "created_at": datetime.now(),
            "message_count": 0
        }

        logger.info(f"Retrieved conversation history for session: {session_id}")
        return history

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/history/{session_id}")
async def clear_conversation_history(session_id: str):
    """
    Clear conversation history for a session

    Args:
        session_id: Session identifier
    """
    try:
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID required")

        # In a real app, delete from database
        logger.info(f"Cleared conversation history for session: {session_id}")

        return {
            "status": "success",
            "session_id": session_id,
            "message": "Conversation history cleared"
        }

    except Exception as e:
        logger.error(f"Error clearing conversation history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/new-session")
async def create_new_session():
    """Create a new conversation session"""
    try:
        session_id = str(uuid.uuid4())
        logger.info(f"Created new conversation session: {session_id}")

        return {
            "session_id": session_id,
            "created_at": datetime.now(),
            "status": "ready"
        }

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/backends")
async def get_conversation_status():
    """
    Get conversation AI backend status

    Returns:
        Current and available backends
    """
    try:
        quota_manager = get_quota_manager()
        hf_client = get_huggingface_client()

        return {
            "current_backend": quota_manager.current_backends["ai"].value,
            "available_backends": ["huggingface", "ollama"],
            "quota_status": quota_manager.get_quota_status(),
            "huggingface_status": hf_client.get_status()
        }

    except Exception as e:
        logger.error(f"Error getting backend status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
