# Quick Start Guide

Get your AI Companion System running in minutes!

## Prerequisites Checklist

- [ ] Windows 11
- [ ] NVIDIA RTX 4060 or better GPU
- [ ] 16GB+ RAM
- [ ] 50GB+ free disk space
- [ ] Python 3.10 or 3.11 installed
- [ ] Node.js 18+ installed
- [ ] Latest NVIDIA drivers

## 5-Minute Setup

### 1. Clone and Setup (2 minutes)

```powershell
# Clone repository
git clone <your-repo-url>
cd ai-companion-system

# Run automated setup
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup_windows.ps1
```

### 2. Install Ollama (1 minute)

1. Download from: https://ollama.ai/download
2. Install and start Ollama
3. Download model:
```bash
ollama pull dolphin-mistral:7b-v2.8
```

### 3. Setup Stable Diffusion (2 minutes)

```bash
# Quick clone
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git sd-webui
cd sd-webui
```

Download SDXL model from:
https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/sd_xl_base_1.0.safetensors

Place in: `sd-webui/models/Stable-diffusion/`

Edit `webui-user.bat`, add: `--api --xformers`

### 4. Start Everything

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate
python -m api.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Stable Diffusion:**
```bash
cd sd-webui
webui-user.bat
```

### 5. Open Application

Navigate to: http://localhost:5173

## First Steps

1. **Create a Character**
   - Click "Characters" tab
   - Click "Create Character"
   - Select a preset (e.g., "Girlfriend")
   - Click "Create"

2. **Start Chatting**
   - Click "Chat" on your character
   - Type a message: "Hi! How are you?"
   - Press Enter

3. **Generate an Image**
   - Go to "Gallery" tab
   - Enter prompt: "beautiful sunset over mountains"
   - Select style: "Realistic"
   - Click "Generate"

## Verify Installation

Check system health: http://localhost:8000/health

All services should show "ok":
- ✅ database
- ✅ llm
- ✅ image_generation
- ✅ memory
- ✅ search

## Troubleshooting

### LLM Not Working
```bash
ollama serve
ollama list
ollama pull dolphin-mistral:7b-v2.8
```

### Images Not Generating
1. Make sure SD WebUI is running at http://127.0.0.1:7860
2. Check `webui-user.bat` has `--api` flag
3. Verify SDXL model is downloaded

### Backend Errors
```bash
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Next Steps

- Read [USER_GUIDE.md](docs/USER_GUIDE.md) for features
- Check [INSTALLATION.md](docs/INSTALLATION.md) for details
- See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for issues

## Performance Tips for RTX 4060

1. **Use recommended model**: dolphin-mistral:7b-v2.8
2. **Enable xformers**: `--xformers` flag in SD WebUI
3. **Start with 25 steps**: Increase if needed
4. **1024x1024 resolution**: Optimal for SDXL
5. **Close other GPU apps**: Chrome, games, etc.

## Useful Commands

```bash
# Check GPU
nvidia-smi

# List Ollama models
ollama list

# Test backend
curl http://localhost:8000/health

# Test SD WebUI
curl http://127.0.0.1:7860/sdapi/v1/sd-models
```

## Default Ports

- Frontend: 5173
- Backend API: 8000
- Ollama: 11434
- SD WebUI: 7860

## Data Locations

- Database: `data/companions.db`
- Memories: `data/chromadb/`
- Images: `data/images/`
- Logs: `logs/app.log`

## Support

For issues:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review terminal logs
3. Test each component individually
4. Check health endpoint

Happy chatting! 🚀
