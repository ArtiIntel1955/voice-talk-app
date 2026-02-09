# Voice Talk Application - Quick Start Guide

## Installation (5 minutes)

### Step 1: Install Dependencies

```bash
cd c:\Users\MyAIE\voice-talk-app

# Option A: Using Poetry (recommended)
pip install poetry
poetry install

# Option B: Using pip
pip install -r requirements.txt
```

### Step 2: Download Vosk Model (Required for Offline Speech Recognition)

```bash
# Run setup script
python setup.py

# It will guide you through:
# 1. Creating directories
# 2. Downloading Vosk model (choose small ~50MB)
# 3. Creating .env file
```

**Or manually download:**
1. Visit: https://alphacephei.com/vosk/models
2. Download: `vosk-model-small-en-us-0.15.zip` (50MB)
3. Extract to: `models/vosk_models/model`

### Step 3: Configure API Keys (Optional, for Cloud Features)

Create `.env` file in project root:

```env
# Get from: https://huggingface.co/settings/tokens
STT_HUGGINGFACE_API_KEY=hf_xxxxx
AI_HUGGINGFACE_API_KEY=hf_xxxxx

# Get from: https://portal.azure.com (Speech Services)
TTS_AZURE_API_KEY=xxxxx
TTS_AZURE_REGION=eastus
```

**Note**: Without API keys, the app works offline with Vosk + Pyttsx3

---

## Usage

### Option 1: Interactive Conversation Mode

Start a voice conversation with intelligent AI responses:

```bash
python cli.py talk
```

Features:
- Type messages and get AI responses
- Responses are spoken aloud
- Real-time conversation history
- Automatic API quota tracking

Example:
```
You: Hello, how are you?
Assistant: I'm doing well, thank you for asking. How can I help you today?
(Audio speaker plays: "I'm doing well, thank you for asking...")

You: Tell me a joke
Assistant: Why did the scarecrow win an award? Because he was outstanding in his field!

You: exit
Goodbye!
```

### Option 2: FastAPI Server

Start the REST API server:

```bash
python cli.py server
# or
python main.py
```

Server runs at: `http://127.0.0.1:8000`

**API Endpoints:**

#### Speech Recognition
```bash
# List audio devices
curl http://127.0.0.1:8000/api/speech/devices

# Get STT status
curl http://127.0.0.1:8000/api/speech/status
```

#### Text-to-Speech
```bash
# List voices
curl http://127.0.0.1:8000/api/voice/voices

# Preview voice
curl "http://127.0.0.1:8000/api/voice/preview?voice=default&text=Hello"

# Get TTS status
curl http://127.0.0.1:8000/api/voice/status
```

#### Conversations
```bash
# Start chat
curl -X POST http://127.0.0.1:8000/api/conversation/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'

# Get conversation history
curl http://127.0.0.1:8000/api/conversation/history/test

# Create new session
curl -X POST http://127.0.0.1:8000/api/conversation/new-session

# Get backend status
curl http://127.0.0.1:8000/api/conversation/backends
```

#### Voice Commands
```bash
# List commands
curl http://127.0.0.1:8000/api/commands/list

# Search command
curl -X POST http://127.0.0.1:8000/api/commands/search?query=open%20notepad

# Execute command
curl -X POST http://127.0.0.1:8000/api/commands/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "open", "parameters": {"target": "notepad"}}'
```

#### Audio Files
```bash
# Upload audio
curl -F "file=@audio.wav" http://127.0.0.1:8000/api/audio/upload

# Transcribe file
curl -X POST http://127.0.0.1:8000/api/audio/transcribe/file_id

# Get audio info
curl http://127.0.0.1:8000/api/audio/info/file_id

# Delete file
curl -X DELETE http://127.0.0.1:8000/api/audio/delete/file_id
```

### Option 3: Transcribe Audio Files

Convert audio files to text:

```bash
# Transcribe to text
python cli.py transcribe --file audio.wav --format txt

# Transcribe to SRT (subtitles)
python cli.py transcribe --file audio.wav --format srt

# Transcribe to JSON
python cli.py transcribe --file audio.wav --format json
```

Supported formats: WAV, MP3, FLAC, OGG, M4A

### Option 4: Check Application Status

```bash
python cli.py status
```

Shows:
- Engine initialization status
- Available voices
- API quota usage
- Current backend selection
- Audio device status

### Option 5: List Audio Devices

```bash
python cli.py list-devices
```

Shows all available microphones and speakers with device indices for configuration.

---

## API Documentation

### Interactive Swagger UI

When server is running, visit:
```
http://127.0.0.1:8000/docs
```

### Full API Endpoints

**Base URL**: `http://127.0.0.1:8000/api`

#### Conversation
- `POST /conversation/chat` - Send message to AI
- `GET /conversation/history/{session_id}` - Get conversation history
- `DELETE /conversation/history/{session_id}` - Clear history
- `POST /conversation/new-session` - Create new session
- `GET /conversation/backends` - Get backend status

#### Speech Recognition
- `POST /speech/transcribe` - Transcribe audio (base64)
- `POST /speech/status` - Get STT engine status
- `POST /speech/devices` - List audio devices

#### Text-to-Speech
- `POST /voice/speak` - Convert text to speech
- `GET /voice/voices` - List available voices
- `GET /voice/preview` - Preview voice
- `GET /voice/status` - Get TTS engine status

#### Voice Commands
- `POST /commands/execute` - Execute a command
- `GET /commands/list` - List all commands
- `POST /commands/search` - Search for command

#### Audio Files
- `POST /audio/upload` - Upload audio file
- `POST /audio/transcribe/{file_id}` - Transcribe file
- `POST /audio/convert/{file_id}` - Convert audio format
- `GET /audio/info/{file_id}` - Get file info
- `DELETE /audio/delete/{file_id}` - Delete file

---

## Features Overview

### Speech Recognition (Offline & Online)
- **Vosk** (Offline): <1s latency, works without internet
- **Hugging Face** (Online): Higher accuracy when available

### Text-to-Speech (Offline & Online)
- **Pyttsx3** (Offline): Always available, Windows native
- **Azure TTS** (Online): Professional quality with API key

### Conversational AI (Cloud & Local)
- **Hugging Face API** (Cloud): Primary, uses free tier quota
- **Ollama** (Local): Fallback when HF quota exceeded
- **Smart Switching**: Automatically detects quota limits

### Voice Commands
Built-in commands:
- `open {app}` - Launch applications
- `search for {query}` - Web search
- `set timer for {duration}` - Set reminder

### File Processing
- Upload audio files
- Automatic transcription
- Format conversion (WAV, MP3, FLAC, OGG)
- Export to SRT, TXT, JSON

---

## Troubleshooting

### "Vosk not initialized"
```bash
# Download Vosk model
python setup.py
# Choose option 1 (small model)
```

### "HuggingFace API not configured"
- Add API key to `.env` file: `AI_HUGGINGFACE_API_KEY=your_token`
- Visit: https://huggingface.co/settings/tokens
- Free tier allows ~1000 calls/day
- Offline fallback works automatically

### Microphone not detected
```bash
# Check available devices
python cli.py list-devices

# Set device index in .env
AUDIO_DEVICE_INDEX=1
```

### No sound output
- Check speakers in Windows Settings
- Use `cli.py list-devices` to verify output device
- Test with: `python cli.py talk`

### Slow transcription
- Vosk is optimized for real-time (<1s/chunk)
- File transcription processes 5-second chunks
- Larger files take longer

### API rate limit (429)
- Free HuggingFace tier: ~1000 requests/day
- App automatically uses local Vosk/Pyttsx3
- Quota resets daily at UTC
- Upgrade HuggingFace account for higher limits

---

## Configuration

### Environment Variables (.env)

```env
# API Keys
STT_HUGGINGFACE_API_KEY=your_token
AI_HUGGINGFACE_API_KEY=your_token
TTS_AZURE_API_KEY=your_key
TTS_AZURE_REGION=eastus

# Audio Settings
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_DEVICE_INDEX=

# Server Settings
HOST=127.0.0.1
PORT=8000
DEBUG=false

# Logging
LOG_LEVEL=INFO
```

### Settings File (src/config/settings.py)

- Audio capture settings
- STT engine configuration
- TTS voice selection
- AI model selection
- Database & cache settings

---

## Command Reference

```bash
# Start interactive conversation
python cli.py talk

# Start REST API server
python cli.py server

# Transcribe audio file
python cli.py transcribe --file audio.wav

# Show application status
python cli.py status

# List audio devices
python cli.py list-devices

# Show all commands
python cli.py --help
```

---

## Performance Tips

1. **Enable GPU** (if available):
   - Improves transcription speed
   - Requires CUDA/GPU support

2. **Use small models first**:
   - Vosk small ≈50MB, ~20k words
   - Ollama small: Phi-3 (~2GB)

3. **Cache responses**:
   - App caches conversation responses
   - Reduces API calls

4. **Batch transcription**:
   - Processes files in 5-second chunks
   - More efficient than real-time

---

## Next Steps

1. ✓ Install dependencies
2. ✓ Download Vosk model
3. ✓ Configure API keys (optional)
4. → Try interactive mode: `python cli.py talk`
5. → Start server: `python cli.py server`
6. → Explore API at http://127.0.0.1:8000/docs

---

## Support Resources

- **Documentation**: See README.md
- **API Docs**: http://127.0.0.1:8000/docs (when running)
- **Models**: https://alphacephei.com/vosk/models
- **Vosk GitHub**: https://github.com/alphacephei/vosk-api
- **HuggingFace**: https://huggingface.co/
- **Ollama**: https://ollama.ai/

---

**Version**: 0.1.0
**Status**: Ready to Use
**Last Updated**: 2024-02-09
