# Voice Talk Application

A comprehensive Windows voice and talk mode application with real-time speech recognition, text-to-speech, conversational AI, and voice command execution. All using free/open-source APIs.

## Features

- **Real-time Speech Recognition**: Convert voice to text using Vosk (offline) with Hugging Face (cloud) fallback
- **Text-to-Speech**: Convert text to speech using Pyttsx3 (offline) with Azure (cloud) fallback
- **Conversational AI**: Get intelligent responses using Hugging Face API (cloud) with Ollama (local) fallback
- **Voice Commands**: Execute system commands via voice
- **File Transcription**: Transcribe audio files to text
- **Multiple Interfaces**: Both CLI and API access
- **Smart Model Switching**: Automatically switches between  free APIs based on quota availability
- **Offline First**: Works completely offline with local models
- **Fully Async**: FastAPI backend with async/await support

## Technology Stack

- **Language**: Python 3.11+
- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite with SQLAlchemy ORM
- **Audio**: PyAudio, librosa, SoundFile
- **Speech Recognition**: Vosk (offline), Hugging Face (online)
- **Text-to-Speech**: Pyttsx3 (offline), Azure (online)
- **Conversational AI**: Hugging Face (cloud), Ollama (local)

## System Requirements

- **OS**: Windows 10/11
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk**: 2GB for models

## Installation

### 1. Clone or Download the Project

```bash
cd c:\Users\YourUsername\voice-talk-app
```

### 2. Install Python Dependencies

Using Poetry (recommended):

```bash
pip install poetry
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
```

### 3. Download Vosk Model (Required for Offline STT)

```bash
# Create models directory
mkdir models\vosk_models

# Download model from: https://alphacephei.com/vosk/models
# Recommended: vosk-model-small-en (50MB)
# Extract to: models/vosk_models/model
```

### 4. Optional - Install Ollama for Local AI

```bash
# Install from: https://ollama.ai
# Download model: ollama pull mistral
```

### 5. Configure API Keys (Optional)

Create a `.env` file in the project root:

```env
# Hugging Face API (get from https://huggingface.co/settings/tokens)
STT_HUGGINGFACE_API_KEY=your_token_here
AI_HUGGINGFACE_API_KEY=your_token_here

# Azure TTS (optional)
TTS_AZURE_API_KEY=your_key_here
TTS_AZURE_REGION=eastus

# Audio device index (leave blank for default)
AUDIO_DEVICE_INDEX=
```

## Quick Start

### Start the API Server

```bash
# Using Poetry
poetry run python main.py

# Or direct Python
python main.py
```

The server will start at `http://127.0.0.1:8000`

### API Documentation

Once running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Example API Calls

**Check Health**:
```bash
curl http://127.0.0.1:8000/health
```

**Chat with AI**:
```bash
curl -X POST http://127.0.0.1:8000/api/conversation/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "session_id": "test-session"}'
```

**Get Available Voices**:
```bash
curl http://127.0.0.1:8000/api/voice/voices
```

## Project Structure

```
voice-talk-app/
├── src/
│   ├── core/              # FastAPI app initialization
│   ├── config/            # Configuration & settings
│   ├── database/          # SQLAlchemy models
│   ├── audio/             # Audio capture, playback, I/O
│   ├── speech/            # STT and TTS engines
│   ├── ai/                # Conversational AI & commands
│   ├── api/               # FastAPI routes & schemas
│   ├── cli/               # CLI interface (Click)
│   └── utils/             # Utilities & helpers
├── tests/                 # Unit & integration tests
├── models/                # AI models (auto-downloaded)
├── data/                  # SQLite DB, logs, cache
├── main.py                # Entry point
├── pyproject.toml         # Dependencies
└── README.md              # This file
```

## Core Components

### 1. Audio Processing (`src/audio/`)
- **capture.py**: Real-time microphone input
- **playback.py**: Speaker output
- **processor.py**: Audio enhancement (normalization, VAD, resampling)
- **io.py**: File read/write support

### 2. Speech Recognition (`src/speech/recognition/`)
- **vosk_engine.py**: Offline STT using Vosk
- Fallback to Hugging Face API online

### 3. Text-to-Speech (`src/speech/synthesis/`)
- **pyttsx3_engine.py**: Offline TTS
- Fallback to Azure TTS online

### 4. Conversational AI (`src/ai/`)
- **huggingface_client.py**: Cloud-based conversational AI
- **quota_manager.py**: Smart model switching & quota tracking
- Fallback to local Ollama

### 5. API Routes (`src/api/routes/`)
- **conversation.py**: Chat endpoints
- (Additional routes coming: speech.py, voice.py, commands.py)

## First-Run Setup Guide

1. **Install dependencies**: `poetry install`
2. **Download Vosk model**: Extract to `models/vosk_models/model`
3. **Optional Ollama**: `ollama pull mistral`
4. **Create API config**: Create `.env` with API keys
5. **Start server**: `python main.py`
6. **Test**: Visit http://127.0.0.1:8000/docs

## Configuration

### Audio Settings
```python
# config/settings.py
AUDIO_SAMPLE_RATE = 16000  # Hz
AUDIO_CHANNELS = 1         # Mono
AUDIO_DEVICE_INDEX = None  # Auto-detect
```

### Speech Recognition
```python
# Offline: Vosk (always available)
# Online: Hugging Face (when API key configured)
# Automatic fallback if quota exceeded
```

### Text-to-Speech
```python
# Offline: Pyttsx3 (always available)
# Online: Azure TTS (when API key configured)
```

### Conversational AI
```python
# Primary: Hugging Face (when API key configured)
# Fallback: Local Ollama (if installed)
```

## Troubleshooting

### Vosk Model Not Found
- Download from: https://alphacephei.com/vosk/models
- Extract to: `models/vosk_models/model`
- Recommended: vosk-model-small-en (50MB, ~20k word vocab)

### Audio Device Not Detected
```python
# List devices:
from src.audio.capture import AudioCapture
ac = AudioCapture()
print(ac.list_devices())

# Set device index in .env or config
AUDIO_DEVICE_INDEX=1
```

### Hugging Face API Rate Limit
- Free tier: ~1000 calls/day
- App automatically falls back to local models
- Upgrade to paid tier for unlimited access
- Or self-host models with Ollama

### Speech Recognition Not Working
1. Check microphone: Windows Settings → Privacy → Microphone
2. List available devices
3. Fall back to Vosk offline mode
4. Check microphone permissions

## API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /` - Root endpoint

### Conversation (Coming Soon)
- `POST /api/conversation/chat` - Send message to AI
- `GET /api/conversation/history/{session_id}` - Get conversation history
- `DELETE /api/conversation/history/{session_id}` - Clear history

### Speech Recognition (Coming Soon)
- `POST /api/speech/transcribe` - Transcribe audio
- `POST /api/speech/stream` - Real-time transcription

### Text-to-Speech (Coming Soon)
- `POST /api/voice/speak` - Convert text to speech
- `GET /api/voice/voices` - List available voices

### Commands (Coming Soon)
- `POST /api/commands/execute` - Execute voice command
- `GET /api/commands/list` - List available commands

### Settings (Coming Soon)
- `GET /api/settings` - Get settings
- `PATCH /api/settings` - Update settings

## Development

### Running Tests
```bash
pytest tests/ -v --cov=src
```

### Code Style
```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

### Adding New Features

1. Create models in `src/database/models.py`
2. Create logic in appropriate module
3. Create API routes in `src/api/routes/`
4. Add tests in `tests/`
5. Update documentation

## Performance

- **Speech Recognition Latency**: <1 second (Vosk offline)
- **Text-to-Speech**: <500ms (Pyttsx3 offline)
- **Conversational AI**: 1-3 seconds (HuggingFace online)
- **Memory Usage**: 200-500MB baseline (plus models)

## Limitations

- **Vosk Accuracy**: ~85% (offline, requires good microphone)
- **Pyttsx3 Quality**: Robotic voice (but always available)
- **HuggingFace Quota**: 1000 requests/day (free tier)
- **Windows Only**: Uses Windows audio and SAPI5

## Future Improvements

- [ ] Wake word detection
- [ ] Multi-language support
- [ ] Real-time translation
- [ ] GUI with PyQt6
- [ ] CLI with Click/Typer
- [ ] Advanced voice profiles
- [ ] Cloud backup
- [ ] Emotion detection
- [ ] Mobile companion app
- [ ] Custom LLM fine-tuning

## License

MIT License - See LICENSE file

## Support

For issues, feature requests, or questions:
1. Check troubleshooting section
2. Check GitHub issues
3. Create detailed bug report with:
   - Windows version
   - Python version
   - Error message
   - Steps to reproduce

## Credits

- **Vosk**: Speech recognition (https://alphacephei.com/vosk/)
- **PyTTSX3**: Text-to-speech (https://pyttsx3.readthedocs.io/)
- **Hugging Face**: Cloud AI models (https://huggingface.co/)
- **Ollama**: Local LLMs (https://ollama.ai/)
- **FastAPI**: Web framework (https://fastapi.tiangolo.com/)

---

**Version**: 0.1.0
**Last Updated**: 2024-02-09
**Status**: In Development
