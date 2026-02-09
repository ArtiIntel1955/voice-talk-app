# Voice Talk GUI - User Guide

Welcome to the Voice Talk Application! This guide covers all features of the professional desktop GUI application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Main Window](#main-window)
3. [Voice Recording](#voice-recording)
4. [Chat Features](#chat-features)
5. [Settings](#settings)
6. [System Tray](#system-tray)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Getting Started

### Launching the Application

**Option 1: Using CLI**
```bash
python cli.py gui
```

**Option 2: Direct Python**
```bash
python gui.py
```

**Option 3: Standalone Executable (After Building)**
```bash
VoiceTalkApp.exe
```

### First Time Setup

1. **Download Vosk Model**: The first time you use voice recording, the app will prompt you to download the offline speech recognition model (~50MB)
   - Choose "Download" to proceed
   - Model is stored in `models/vosk_models/`

2. **Configure API Keys (Optional)**
   - For cloud features, open Settings and add your API keys
   - Currently supports HuggingFace (AI conversations)
   - Azure (optional advanced TTS)
   - Google Cloud (optional advanced features)

3. **Test Your Setup**
   - Click "Advanced Settings"
   - Go to "API" tab
   - Click "Test API Connection"

---

## Main Window

The application window is divided into three main sections:

### Left Panel: Chat Display

**Conversation History**
- Shows all messages in chronological order
- Each message includes timestamp, speaker name, and content
- Messages appear in real-time as you interact
- Format: `[HH:MM:SS] Speaker: Message`

**Example**:
```
[14:23:45] You: What is the capital of France?
[14:23:47] Assistant: The capital of France is Paris.
```

### Right Panel: Controls & Status

**Voice Selection**
- Dropdown menu to choose from available system voices
- Changes apply immediately
- Available voices depend on Windows language pack

**Speech Speed**
- Slider: 50 (Very Slow) to 200 (Very Fast)
- Default: 150 (Normal)
- Visual indicator shows current speed level
- Useful for accessibility and preference

**API Status**
- **AI Backend**: Shows which service is currently active
  - "HuggingFace" (default)
  - "Ollama" (if fallback needed)
  - "Local" (offline mode)
- **Daily Quota**: Total API calls allowed
- **Remaining**: Calls left today
- Status bar updates automatically every 30 seconds

**Buttons**
- ⚙️ **Advanced Settings**: Opens configuration dialog
- **Clear History**: Removes all messages from chat display

---

## Voice Recording

### How to Record Voice Input

1. **Click "🎤 Record Voice" Button**
   - Status bar shows: "Recording... (5 seconds)"
   - Red indicator "🔴 RECORDING" appears
   - Status updates show progress and transcribed text

2. **Speak Your Message**
   - Speak clearly and naturally
   - The app transcribes in real-time using Vosk
   - Partial transcriptions update as you speak

3. **Recording Automatically Stops After 5 Seconds**
   - Or press ESC (future enhancement)
   - Transcribed text appears in input field
   - Message automatically sends to AI

### Voice Recording Tips

- **Speak Clearly**: Avoid mumbling for better accuracy
- **Quiet Environment**: Background noise reduces accuracy
- **Microphone Position**: 6-12 inches from your mouth
- **One Sentence Per Recording**: Better results than long monologues

### Troubleshooting Voice Recording

**"Failed to start audio capture"**
- Check microphone is connected
- No other application is using microphone
- Try different microphone in Settings

**"No speech detected"**
- Speak louder
- Move microphone closer
- Check microphone volume in Windows

**Transcription is Inaccurate**
- Use shorter, simpler sentences
- Speak more slowly and clearly
- Check if Vosk model is properly downloaded

---

## Chat Features

### Sending Text Messages

1. **Type Your Message** in the text input area
2. **Click "Send Message" Button** or:
   - Press `Ctrl+Enter` (if implemented)
   - Press `Enter` (if single-line mode)

3. **Message Will**:
   - Appear in chat with "[HH:MM:SS] You: Message"
   - Be sent to AI backend
   - Get a response within 1-10 seconds

### AI Response Features

**Automatic TTS**
- AI responses are automatically read aloud
- Uses selected voice (right panel)
- Speech speed respects your slider setting
- Can be toggled in Settings (future)

**Response Quality**
- First 500 characters read aloud
- Full response visible in chat window
- Responses cached for offline replay (future)

**Error Handling**
- Network errors show friendly messages
- API quota exceeded? → Falls back to local AI
- Connection lost? → Uses cached responses

---

## Settings

### Opening Settings

Click **"⚙️ Advanced Settings"** button in right panel

### Audio Tab

**Input Device**
- Dropdown: "Default" or specific microphone
- Click dropdown to see detected microphones
- Changes take effect on next recording

**Output Device**
- Dropdown: "Default" or specific speaker
- Select for TTS playback
- Test sound plays through selected device

**Sample Rate**
- Options: 16000Hz (Recommended), 48000Hz, 44100Hz
- 16000Hz: Best for voice recognition
- Higher rates: Better audio quality but larger files

**Volume**
- Slider: 0-100 (percentage of system volume)
- Affects TTS playback volume only
- Doesn't affect microphone sensitivity

### API Tab

**HuggingFace Token**
- Masked input field (password-like)
- Paste your API key from huggingface.co
- Test connection with "Test API Connection" button
- Required for cloud AI features

**Azure Region** (Optional)
- Dropdown with Azure region codes
- Examples: "eastus", "westeurope", "japaneast"
- Only needed if using Azure TTS

**Google Credentials** (Optional)
- File browser to select Google Cloud JSON credentials
- Only needed for advanced Google Cloud features

**Test API Connection**
- Tests current API configuration
- Shows success/failure message
- Helpful for debugging setup issues

### Appearance Tab

**Theme**
- Dropdown: "Light" or "Dark"
- Changes colors and contrast
- Applies immediately
- Persists across restarts

**Font Size**
- Spinner: 8-24 points
- Affects chat display and UI text
- Default: 10 points

**Auto-Save**
- Checkbox: Automatically save messages
- When disabled: History only persists in memory

**Show Timestamps**
- Checkbox: Display time with each message
- Useful for conversation tracking

**Minimize to System Tray**
- Checkbox: Hide to tray on close
- When disabled: Normal close behavior

### Saving Settings

1. **Make Your Changes**
2. **Click "Save Settings"** (dialog bottom)
3. **Confirmation Message**: "All settings saved successfully!"
4. **Settings Persist**: Automatically restored on app restart

---

## System Tray

### Minimize to Tray

When **"Minimize to System Tray"** is enabled in Settings:

1. **Click the X button** → App minimizes to tray (doesn't close)
2. **Click system tray icon** → App window appears
3. **Right-click tray icon**:
   - Show → Restores window
   - Hide → Minimizes to tray
   - Exit → Closes application completely

### Benefits

- Keep app running in background
- Minimize desktop clutter
- Quick access from system tray
- CPU-efficient when minimized

---

## Troubleshooting

### Application Won't Start

**Error: "ModuleNotFoundError: No module named 'PyQt6'"**
- Solution: `pip install PyQt6`

**Error: "ModuleNotFoundError: No module named 'vosk'"**
- Solution: `pip install vosk`

**Error: Port 8000 already in use**
- The FastAPI server might be running
- Solution: `python cli.py server` is already executing
- Kill the server process or use different port

### Chat Not Working

**Messages sent but no responses**
- Check API status indicator
- Try clicking "Test API Connection"
- Ensure internet connection
- Check API key in Settings

**"Daily quota exceeded" message**
- API calls limit reached
- Wait until next day for reset
- Or use local Ollama if configured

### Voice Recording Issues

See [Voice Recording Troubleshooting](#troubleshooting-voice-recording) above

### GUI Freezes

**Freezing during message sending**
- This is normal, usually > 5 seconds
- GUI remains responsive to cancel (future)

**Freezing during voice recording**
- Also normal during 5-second capture
- Click elsewhere to see other UI updates

### Settings Not Saving

**Error: "Failed to save settings"**
- Check write permissions on `data/gui_settings.json`
- Ensure `data/` directory exists
- Try again or restart application

---

## FAQ

### Q: Can I use the app without internet?

**A:** Yes! The app works completely offline with:
- Voice recognition: Vosk offline model
- Text-to-speech: Windows native pyttsx3
- AI responses: Local Ollama (if installed)

Cloud features require internet but will fall back gracefully.

### Q: How do I improve voice recognition accuracy?

**A:**
1. Speak clearly and naturally
2. Use quiet environment
3. Position microphone 6-12 inches away
4. Shorter sentences work better
5. Ensure Vosk model is downloaded

### Q: How do I change my API key?

**A:**
1. Open Advanced Settings
2. Go to API tab
3. Clear and re-enter new key
4. Click "Test API Connection"
5. Click "Save Settings"

### Q: Does the app record my conversations?

**A:**
- Conversations are stored locally in SQLite database
- Location: `data/conversation_history.db`
- Only contains text, not audio
- You can delete at any time
- No data sent to cloud except API requests

### Q: Can I run multiple instances?

**A:** Yes, but:
- Each instance uses independent GUI settings
- They may conflict on microphone/speaker access
- Recommended: Single instance per user

### Q: How much disk space does it need?

**A:**
- Application: ~50-100MB (depends on dependencies)
- Vosk model: ~50MB
- Settings: < 1KB
- Conversation history: Depends on usage (typically < 10MB)
- Total: ~100-200MB

### Q: What voices are available?

**A:** Depends on Windows language packs:
- English: Microsoft David, Zira, Mark (Windows 10+)
- Additional voices available via Windows Settings
- Install language packs for more voices

### Q: Can I integrate with other apps?

**A:** Currently no direct integration, but:
- Use REST API (`python cli.py server`)
- Make HTTP requests to localhost:8000
- See API documentation: http://localhost:8000/docs

### Q: Is there a mobile version?

**A:** Not yet! Currently Windows desktop only.

---

## Advanced Usage

### Using REST API with GUI

The GUI app uses the same FastAPI backend. You can:

1. **Start Server**: `python cli.py server`
2. **Open GUI**: `python cli.py gui` (separate window)
3. **Make HTTP requests** to `http://localhost:8000`

See `API_KEYS_SETUP.md` for API endpoint documentation.

### Viewing Logs

Application logs are stored in:
```
data/logs/voice_talk_*.log
```

Enable detailed logging in Settings (future enhancement).

### Accessing Database

Conversation history is in:
```
data/conversation_history.db
```

Uses SQLite - open with any SQLite browser to view/export conversations.

---

## Support

For issues or feature requests:
1. Check GitHub: https://github.com/ArtiIntel1955/voice-talk-app
2. Review SECURITY_AUDIT_REPORT.md for known issues
3. Check application logs in `data/logs/`

---

**Last Updated**: February 2026
**Application Version**: 0.1.0
**GUI Version**: 1.0.0

Enjoy using Voice Talk! 🎤🗣️
