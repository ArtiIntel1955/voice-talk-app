"""Main Entry Point - Start FastAPI Server"""

import uvicorn
import sys
from pathlib import Path

from src.core.app_instance import create_app
from src.config.settings import get_settings
from src.config.logger import LoggerManager

# Initialize logging
LoggerManager.initialize()

# Create FastAPI app
app = create_app()


def main():
    """Run the FastAPI server"""
    settings = get_settings()

    print(f"""
    =====================================
    {settings.app_name} v{settings.version}
    =====================================

    Starting server...
    Host: {settings.host}
    Port: {settings.port}
    Debug: {settings.debug}

    API Docs: http://{settings.host}:{settings.port}/docs
    ReDoc: http://{settings.host}:{settings.port}/redoc
    """)

    # Run server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )


if __name__ == "__main__":
    main()
