"""FastAPI Application Factory and Initialization"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from ..config.settings import get_settings
from ..config.logger import LoggerManager, get_logger
from ..config.constants import API_PREFIX
from ..database.database import init_database


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Application startup")
    logger.info(f"Initializing database: {get_settings().database.db_path}")
    await init_database()

    yield

    # Shutdown
    logger.info("Application shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    # Initialize logging first
    LoggerManager.initialize()
    logger.info("FastAPI Application Initialization Started")

    # Load settings
    settings = get_settings()

    # Create FastAPI instance
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="A comprehensive Windows voice and talk mode application",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.version
        }

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API documentation"""
        return {
            "app_name": settings.app_name,
            "version": settings.version,
            "docs_url": "/docs",
            "openapi_url": "/openapi.json"
        }

    # Include API routes
    from ..api.routes import conversation, speech, voice, audio, commands

    app.include_router(conversation.router)
    app.include_router(speech.router)
    app.include_router(voice.router)
    app.include_router(audio.router)
    app.include_router(commands.router)

    logger.info(f"FastAPI Application created: {settings.app_name} v{settings.version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server: {settings.host}:{settings.port}")
    logger.info(f"API Routes registered: conversation, speech, voice, audio, commands")

    return app


def get_app() -> FastAPI:
    """Get or create the FastAPI application instance"""
    return create_app()
