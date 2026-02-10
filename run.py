#!/usr/bin/env python
"""Wrapper script to run the voice-talk-app with static files"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.app_instance import create_app

app = create_app()

# Serve the voice assistant UI
@app.get("/")
async def serve_voice_ui():
    """Serve the voice assistant web interface"""
    return FileResponse(Path(__file__).parent / "index.html")

# Mount static files if needed
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
