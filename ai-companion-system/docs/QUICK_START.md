# Quick Start Guide

Get up and running with AI Companion System in minutes!

## Prerequisites Installed?

Make sure you have:
- ✅ Python 3.10/3.11
- ✅ Node.js 18+
- ✅ Ollama with dolphin-mistral model
- ✅ Stable Diffusion WebUI (optional for images)

If not, see [INSTALLATION.md](INSTALLATION.md)

## Quick Setup (5 minutes)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Start Services

**Option A: Use Scripts (Recommended)**
- Double-click `scripts/start_backend.bat`
- Double-click `scripts/start_frontend.bat`
- (Optional) Start Stable Diffusion WebUI with `--api` flag

**Option B: Manual Start**

Terminal 1 - Backend:
```bash
cd backend
venv\Scripts\activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### 4. Open Application

Go to: **http://localhost:5173**

## First Time Usage

### Create Your First Character

1. Click **"+ New Character"** button
2. Choose a template:
   - **Emma** - Virtual girlfriend (romantic, caring)
   - **Dr. Sarah** - Therapist (professional, helpful)
   - **Alex** - Best friend (casual, funny)
   - **Luna** - Creative muse (artistic, inspiring)

3. Start chatting!

### Enable Image Generation

1. Start Stable Diffusion WebUI:
   ```bash
   cd stable-diffusion-webui
   webui-user.bat
   ```

2. Make sure `--api` flag is enabled in `webui-user.bat`

3. Go to **Gallery** tab in the app
4. Enter a prompt and click **Generate**

## Features Overview

### Chat Features
- 💬 Real-time streaming responses
- 🧠 Long-term memory (remembers conversations)
- 🌐 Web search integration (for current info)
- 🎭 Character-specific personalities

### Image Generation
- 🎨 Multiple styles (realistic, anime, manga)
- 🚫 Uncensored generation
- 🖼️ Character-specific images
- 💾 Image gallery with history

### Character Management
- 📝 Create custom characters
- 🎭 Pre-made templates
- 🔧 Customize appearance, personality, backstory
- 💾 Multiple characters support

## Tips & Tricks

### Performance
- Close other GPU apps for better performance
- Use 20-30 steps for faster image generation
- Keep conversation history reasonable (cleared automatically)

### Chat
- Characters can suggest generating images during chat
- Memories persist across sessions
- Clear history anytime from chat interface

### Images
- Try different styles for varied results
- "Generate Character" button creates character portraits
- All images saved locally in `data/images/`

## Troubleshooting

### "LLM not available"
```bash
ollama pull dolphin-mistral:7b-v2.8
```

### "SD API not available"
- Start SD WebUI with `--api` flag
- Check it's running on port 7860

### "Backend not starting"
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### "Frontend not loading"
```bash
cd frontend
npm install
```

## What's Next?

- **Customize Characters**: Edit personality, appearance, backstory
- **Generate Images**: Create character portraits and scenes
- **Explore Memory**: Characters remember your conversations
- **Try Web Search**: Ask characters about current events

## Need Help?

- Full installation guide: [INSTALLATION.md](INSTALLATION.md)
- Detailed features: [USER_GUIDE.md](USER_GUIDE.md)
- Common issues: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Enjoy your AI Companion System!** 🎉
