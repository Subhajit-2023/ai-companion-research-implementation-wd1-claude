# Voice Chat Feature Guide

Complete guide to using voice chat with Text-to-Speech (TTS) and Speech-to-Text (STT) in the AI Companion System.

## Overview

The voice chat feature allows you to have natural voice conversations with your AI companions using completely free, local technology.

### Key Features

- **Text-to-Speech (TTS)**: Characters speak their responses out loud
- **Speech-to-Text (STT)**: Talk to characters using your microphone
- **Multiple Voices**: 7+ high-quality voices to choose from
- **Voice Customization**: Set unique voices for each character
- **Speed Control**: Adjust speech speed from 0.5x to 2.0x
- **100% Free & Local**: No API keys, no subscriptions, complete privacy

## Technology

### Piper TTS
- **What**: High-quality neural text-to-speech
- **Quality**: Near-human voice quality
- **Speed**: Fast generation (0.5-2 seconds)
- **Voices**: Multiple male, female, and neutral voices
- **Languages**: English (US/UK) and more
- **License**: Free and open-source

### Whisper STT
- **What**: OpenAI's state-of-the-art speech recognition
- **Accuracy**: 95%+ for clear speech
- **Languages**: 99+ languages supported
- **Models**: Multiple sizes (tiny to large)
- **Processing**: Local, no cloud API needed
- **License**: Free and open-source

## Installation

### Prerequisites

- Python 3.10 or higher
- 2GB RAM minimum (4GB+ recommended for STT)
- Storage: 500MB - 2GB for models
- (Optional) NVIDIA GPU for faster STT

### Step 1: Install Piper TTS

**Linux**:
```bash
# Download Piper
wget https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz

# Extract
tar -xzf piper_linux_x86_64.tar.gz

# Install
sudo mv piper /usr/local/bin/
sudo chmod +x /usr/local/bin/piper

# Verify
piper --version
```

**Windows**:
1. Download from: https://github.com/rhasspy/piper/releases/latest
2. Download `piper_windows_amd64.zip`
3. Extract to a folder (e.g., `C:\Program Files\Piper`)
4. Add folder to PATH environment variable
5. Open new terminal and verify: `piper --version`

**macOS**:
```bash
# Download Piper
wget https://github.com/rhasspy/piper/releases/latest/download/piper_macos_x86_64.tar.gz

# Extract
tar -xzf piper_macos_x86_64.tar.gz

# Install
sudo mv piper /usr/local/bin/
sudo chmod +x /usr/local/bin/piper

# Verify
piper --version
```

### Step 2: Download Voice Models

Voice models need to be downloaded separately.

**Quick Start - Download Essential Voices**:
```bash
cd ai-companion-system/backend/data
mkdir -p tts_models
cd tts_models

# Female voice (Amy - US)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json

# Male voice (Danny - US)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/danny/low/en_US-danny-low.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/danny/low/en_US-danny-low.onnx.json

# High quality (LibriTTS)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx.json
```

**All Available Voices**:

Visit: https://rhasspy.github.io/piper-samples/

Download any voices you want. Each voice needs two files:
- `{voice-name}.onnx` - The model file
- `{voice-name}.onnx.json` - The config file

Place both files in `backend/data/tts_models/`

### Step 3: Install Python Dependencies

```bash
cd ai-companion-system/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install voice dependencies
pip install faster-whisper torch torchaudio soundfile
```

Whisper models download automatically on first use.

### Step 4: Verify Installation

Start the backend:
```bash
python api/main.py
```

Check voice services:
```bash
curl http://localhost:8000/api/voice/health
```

Expected response:
```json
{
  "tts": {
    "available": true,
    "piper_installed": true,
    "voices_downloaded": 3
  },
  "stt": {
    "available": true,
    "model_loaded": true,
    "model_info": {...}
  }
}
```

## Usage

### Enable Voice for a Character

1. Go to **Characters** tab
2. Select a character
3. Click character card settings/options
4. Open **Voice Settings**
5. Toggle **Enable Voice** on
6. Select a voice from dropdown
7. Adjust speed if desired (default 1.0x)
8. Click **Test Voice** to preview
9. Save settings

### Voice Chat

**Speaking (TTS)**:
- When voice is enabled, character responses play automatically
- Audio control buttons appear on messages
- Click play icon to replay
- Click stop to pause audio

**Listening (STT)**:
- Click microphone button in chat input
- Allow microphone access when prompted
- Speak your message clearly
- Click stop when done
- Transcribed text appears in input
- Edit if needed, then send

### Voice Settings

**Per-Character Settings**:
- **Voice ID**: Which voice model to use
- **Enabled**: Turn voice on/off
- **Speed**: Speech rate (0.5x slow to 2.0x fast)

**Global Settings**:
- Whisper model size (quality vs speed tradeoff)
- Audio cache duration
- Auto-play behavior

## Available Voices

### Female Voices

**Amy (en_US-amy-medium)**:
- Gender: Female
- Accent: American
- Quality: Medium
- Description: Warm, friendly voice
- Best for: Girlfriend, friend personas

**Lessac (en_US-lessac-medium)**:
- Gender: Female
- Accent: American
- Quality: Medium
- Description: Clear, professional
- Best for: Therapist, professional personas

**Alba (en_GB-alba-medium)**:
- Gender: Female
- Accent: British
- Quality: Medium
- Description: Gentle, sophisticated
- Best for: Creative muse, elegant characters

### Male Voices

**Danny (en_US-danny-low)**:
- Gender: Male
- Accent: American
- Quality: Low (fast)
- Description: Clear male voice
- Best for: Friend, casual personas

**Ryan (en_US-ryan-medium)**:
- Gender: Male
- Accent: American
- Quality: Medium
- Description: Deep, professional
- Best for: Mentor, authority figures

**Northern English Male (en_GB-northern_english_male-medium)**:
- Gender: Male
- Accent: British (Northern)
- Quality: Medium
- Description: Distinctive northern accent
- Best for: Unique character voices

### Neutral/High Quality

**LibriTTS (en_US-libritts-high)**:
- Gender: Neutral
- Accent: American
- Quality: High
- Description: Natural, high-quality
- Best for: Any persona, highest quality

## Whisper Models

Choose model size based on your needs:

| Model | Size | VRAM | Speed | Accuracy | Use Case |
|-------|------|------|-------|----------|----------|
| tiny | 39 MB | ~1 GB | Very Fast | Good | Quick responses |
| base | 74 MB | ~1 GB | Fast | Better | **Recommended** |
| small | 244 MB | ~2 GB | Medium | Good | Quality priority |
| medium | 769 MB | ~5 GB | Slower | High | High accuracy |
| large-v2 | 1550 MB | ~10 GB | Slow | Highest | Maximum quality |

### Change Model Size

Via API:
```bash
curl -X POST http://localhost:8000/api/voice/stt/model/change \
  -H "Content-Type: application/json" \
  -d '{"model_size": "small"}'
```

Or edit `backend/.env`:
```env
WHISPER_MODEL_SIZE=small
```

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# Piper TTS Settings
PIPER_PATH=piper  # Path to Piper binary

# Whisper STT Settings
WHISPER_MODEL_SIZE=base      # tiny, base, small, medium, large-v2
WHISPER_DEVICE=auto          # auto, cpu, cuda
WHISPER_COMPUTE_TYPE=int8    # int8, float16, float32 (affects speed/quality)
```

### Voice Model Storage

```
backend/data/
├── tts_models/          # Piper voice models (.onnx files)
├── tts_audio/           # Generated audio cache
└── whisper_models/      # Whisper models (auto-downloaded)
```

### Cache Management

TTS audio is cached for performance. Clean old files:

```python
from api.services.tts_service import tts_service

# Clean files older than 7 days
tts_service.cleanup_old_audio(max_age_days=7)
```

## Performance Optimization

### TTS Performance

**Fast Generation**:
- Use "low" quality voices (e.g., danny-low)
- Lower speech speed
- Enable audio caching

**High Quality**:
- Use "high" quality voices (e.g., libritts-high)
- Normal speech speed
- More storage for cache

### STT Performance

**Fast Transcription**:
- Use tiny or base model
- Enable GPU if available
- Use int8 compute type

**High Accuracy**:
- Use medium or large model
- Use float16/float32 compute type
- GPU highly recommended

### GPU Acceleration

**Check GPU availability**:
```python
import torch
print(torch.cuda.is_available())  # Should print: True
```

**Enable GPU for Whisper**:
```env
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
```

## Troubleshooting

### TTS Issues

**Problem**: "Piper not found"
**Solution**:
1. Verify Piper is installed: `piper --version`
2. Check PATH includes Piper directory
3. Try full path in .env: `PIPER_PATH=/usr/local/bin/piper`

**Problem**: "Voice model not found"
**Solution**:
1. Check files exist in `backend/data/tts_models/`
2. Verify both `.onnx` and `.onnx.json` files present
3. File names must match exactly (e.g., `en_US-amy-medium.onnx`)

**Problem**: "Audio generation failed"
**Solution**:
1. Check Piper can run: `piper --version`
2. Test manually: `echo "test" | piper --model path/to/model.onnx --output_file test.wav`
3. Check disk space for audio cache

### STT Issues

**Problem**: "Model download failed"
**Solution**:
1. Check internet connection
2. Models download to `backend/data/whisper_models/`
3. Manually download from Hugging Face if needed

**Problem**: "Out of memory"
**Solution**:
1. Use smaller model (tiny or base)
2. Close other applications
3. Use CPU instead of GPU: `WHISPER_DEVICE=cpu`

**Problem**: "Slow transcription"
**Solution**:
1. Use smaller model
2. Enable GPU if available
3. Use int8 compute type

### Audio Playback

**Problem**: "No audio plays"
**Solution**:
1. Check browser audio not muted
2. Verify audio file exists: Check `/audio/` URL
3. Check browser console for errors (F12)

**Problem**: "Choppy audio"
**Solution**:
1. Increase cache size
2. Use lower quality voice model
3. Check system resources

### Microphone Issues

**Problem**: "Microphone not working"
**Solution**:
1. Grant microphone permission in browser
2. Check system microphone settings
3. Try different browser
4. Verify microphone works in other apps

**Problem**: "Poor transcription accuracy"
**Solution**:
1. Speak clearly and at normal pace
2. Reduce background noise
3. Use larger Whisper model
4. Check microphone quality

## API Reference

### TTS Endpoints

**Synthesize Speech**:
```
POST /api/voice/tts/synthesize
Body: {
  "text": "Hello world",
  "voice_id": "en_US-amy-medium",
  "speed": 1.0
}
Response: {
  "audio_url": "/audio/tts_123.wav",
  "voice_id": "en_US-amy-medium",
  "cached": false
}
```

**List Voices**:
```
GET /api/voice/tts/voices
Response: [
  {
    "voice_id": "en_US-amy-medium",
    "name": "Amy (Female, US)",
    "gender": "female",
    "installed": true
  },
  ...
]
```

### STT Endpoints

**Transcribe Audio**:
```
POST /api/voice/stt/transcribe
Form Data:
  - audio: <audio file>
  - language: "en"
Response: {
  "text": "transcribed text",
  "language": "en",
  "language_probability": 0.99,
  "duration": 5.2
}
```

**List Models**:
```
GET /api/voice/stt/models
Response: {
  "available_models": {...},
  "current_model": {...}
}
```

### Character Voice

**Update Voice Settings**:
```
PUT /api/voice/characters/{id}/voice
Body: {
  "voice_id": "en_US-amy-medium",
  "voice_enabled": true,
  "voice_speed": 1.0
}
```

**Get Voice Settings**:
```
GET /api/voice/characters/{id}/voice
Response: {
  "character_id": 1,
  "voice_settings": {...}
}
```

## Best Practices

### For Best Voice Quality

1. **Choose appropriate voices**: Match voice to character personality
2. **Adjust speed carefully**: Stay close to 1.0x for natural sound
3. **Clear text**: Punctuation affects intonation
4. **Use caching**: Repeated phrases use cached audio

### For Best Transcription

1. **Speak clearly**: Normal pace, clear pronunciation
2. **Reduce noise**: Quiet environment improves accuracy
3. **Use good microphone**: Quality matters
4. **Pause between thoughts**: Helps with sentence detection

### Performance Tips

1. **Start with base model**: Good balance of speed and quality
2. **Enable GPU**: Much faster for Whisper
3. **Cache management**: Clean old audio regularly
4. **Download voices ahead**: Don't wait until needed

## Privacy & Security

### Data Privacy

✅ **All processing is local**:
- No cloud API calls for TTS or STT
- Audio never leaves your device
- No external services required

✅ **Audio storage**:
- TTS audio cached locally only
- You control cache duration
- No audio sent to external servers

✅ **Microphone access**:
- Only when you click microphone button
- Browser controls permissions
- Audio processed locally only

### Security Considerations

- Audio files stored in `backend/data/tts_audio/`
- Automatic cleanup of old files
- No sensitive data in audio filenames
- Local network only by default

## Examples

### Example 1: Enable Voice for Girlfriend Character

```javascript
// Set Luna's voice to warm female voice
await axios.put('/api/voice/characters/1/voice', {
  voice_id: 'en_US-amy-medium',
  voice_enabled: true,
  voice_speed: 1.1  // Slightly faster
});
```

### Example 2: Voice Chat Interaction

```javascript
// 1. Record user speech
const audioBlob = await recordAudio();

// 2. Transcribe to text
const formData = new FormData();
formData.append('audio', audioBlob);
const sttResponse = await axios.post('/api/voice/stt/transcribe', formData);

// 3. Send to character
const chatResponse = await axios.post('/api/chat/send', {
  message: sttResponse.data.text,
  character_id: 1
});

// 4. Generate speech for response
const ttsResponse = await axios.post('/api/voice/tts/synthesize', {
  text: chatResponse.data.response,
  voice_id: character.voice_settings.voice_id
});

// 5. Play audio
const audio = new Audio(ttsResponse.data.audio_url);
audio.play();
```

### Example 3: Test All Voices

```javascript
const voices = await axios.get('/api/voice/tts/voices');

for (const voice of voices.data) {
  if (voice.installed) {
    console.log(`Testing voice: ${voice.name}`);
    const response = await axios.post('/api/voice/tts/synthesize', {
      text: `Hello, I'm ${voice.name}`,
      voice_id: voice.voice_id
    });
    // Play audio to compare
  }
}
```

## FAQ

**Q: Is this really free?**
A: Yes! Both Piper and Whisper are open-source and free. No API keys needed.

**Q: Do I need internet?**
A: Only for initial model downloads. After that, everything works offline.

**Q: How much storage do voices use?**
A: Each voice model is 50-150 MB. Generated audio is cached (~100 KB per sentence).

**Q: Can I use custom voices?**
A: Piper supports custom voices if you have trained models in ONNX format.

**Q: What languages are supported?**
A: Currently English (US/UK). More languages coming with additional Piper models.

**Q: Does this work on mobile?**
A: Backend works anywhere. Browser features (mic, audio) require mobile browser support.

**Q: How accurate is speech recognition?**
A: Whisper achieves 95%+ accuracy for clear speech with base/small models.

**Q: Can I stream audio?**
A: TTS is file-based. STT will support streaming in future version.

## Support

For issues and questions:

1. Check this documentation
2. See `docs/TROUBLESHOOTING.md`
3. Check health endpoint: `/api/voice/health`
4. Review backend logs
5. Test with example audio files

## Resources

- **Piper TTS**: https://github.com/rhasspy/piper
- **Piper Voices**: https://rhasspy.github.io/piper-samples/
- **Whisper**: https://github.com/openai/whisper
- **Faster-Whisper**: https://github.com/guillaumekln/faster-whisper

---

**Enjoy natural voice conversations with your AI companions!** 🎤🔊
