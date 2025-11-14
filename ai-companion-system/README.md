# AI Companion System

A fully open-source, private AI companion system with unrestricted chat, image generation, and advanced character customization capabilities. Designed to run locally on Windows 11 with RTX 4060 GPU.

## Features

### Core Capabilities
- **Unrestricted AI Chat**: Using uncensored LLMs (Dolphin Mistral, WizardLM)
- **AI Image Generation**: NSFW-capable Stable Diffusion XL with LoRA support
- **Character Customization**: Create and customize AI companions with unique personalities, backstories, and appearances
- **Advanced Memory System**: Long-term memory that remembers conversations and learns user preferences
- **Internet Access**: Real-time web search integration for up-to-date information
- **Multiple Characters**: Support for multiple AI companions including specialized roles (therapist, friend, romantic partner)
- **100% Private & Free**: All processing happens locally, no API calls, no data collection

### Technology Stack

#### LLM (Language Models)
- **Primary**: Dolphin 2.9.3 Mistral Nemo 12B (uncensored, optimized for consumer GPUs)
- **Alternative**: WizardLM Uncensored 13B
- **Inference Engine**: Ollama (easy setup and management)
- **Performance**: 40-53 tokens/s on RTX 4060

#### Image Generation
- **Model**: Stable Diffusion XL 1.0
- **LoRAs**: NSFW-capable community models from Civitai
- **VAE**: sdxl-vae-fp16-fix
- **Interface**: Automatic1111 Stable Diffusion WebUI API
- **Performance**: ~3-5 seconds per image on RTX 4060

#### Memory & Context
- **Short-term**: Conversation history with sliding window
- **Long-term**: Mem0 memory layer with vector embeddings
- **Vector Database**: ChromaDB for semantic search
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2

#### Web Access
- **Search Engine**: DuckDuckGo (no API key required)
- **Fallback**: SearXNG metasearch (optional)
- **RAG Integration**: LangChain for document retrieval

#### Backend
- **Framework**: FastAPI
- **Database**: SQLite
- **WebSockets**: For real-time chat
- **Image Storage**: Local filesystem

#### Frontend
- **Framework**: React 18
- **UI Library**: Material-UI / Tailwind CSS
- **State Management**: Zustand
- **Real-time**: Socket.io client

## System Requirements

### Minimum Hardware
- **GPU**: NVIDIA RTX 4060 (8GB VRAM) or better
- **RAM**: 16GB system RAM
- **Storage**: 50GB free space
- **CPU**: Intel i7 or AMD Ryzen 7
- **OS**: Windows 11

### Software Prerequisites
- Python 3.10 or 3.11
- Node.js 18+
- Git
- CUDA 11.8 or 12.1
- NVIDIA GPU Drivers (latest)

## Project Structure

```
ai-companion-system/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   ├── characters.py    # Character management
│   │   │   ├── images.py        # Image generation
│   │   │   └── search.py        # Web search
│   │   ├── models/              # Database models
│   │   ├── services/
│   │   │   ├── llm_service.py   # LLM inference
│   │   │   ├── image_service.py # SD image generation
│   │   │   ├── memory_service.py# Memory management
│   │   │   └── search_service.py# Web search
│   │   └── main.py              # FastAPI app
│   ├── database/
│   │   ├── db.py                # Database setup
│   │   └── migrations/
│   ├── characters/              # Character definitions
│   │   └── presets/
│   ├── requirements.txt
│   └── config.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   ├── CharacterCreator/
│   │   │   ├── Gallery/
│   │   │   └── Settings/
│   │   ├── services/
│   │   ├── store/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── INSTALLATION.md
│   ├── MODELS_SETUP.md
│   ├── TROUBLESHOOTING.md
│   └── USER_GUIDE.md
├── scripts/
│   ├── setup_windows.ps1        # Windows setup script
│   ├── download_models.py       # Model downloader
│   └── test_gpu.py              # GPU test
├── .env.example
└── README.md
```

## Quick Start

See [INSTALLATION.md](docs/INSTALLATION.md) for detailed setup instructions.

### 1. Clone Repository
```bash
git clone <repository-url>
cd ai-companion-system
```

### 2. Setup Python Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Install Ollama & Download Models
```bash
# Download from https://ollama.ai/download
ollama pull dolphin-mistral:7b-v2.8-q4_K_M
```

### 4. Setup Stable Diffusion
```bash
# Clone Automatic1111 WebUI
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git sd-webui
cd sd-webui
# Run webui-user.bat with --api flag
```

### 5. Start Backend
```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 7. Access Application
Open browser to `http://localhost:5173`

## Key Features Explained

### Character System
- Create unlimited custom characters
- Define personality traits, backstory, speaking style
- Assign visual appearance (for image generation)
- Pre-configured characters: Girlfriend, Therapist, Friend, etc.

### Memory System
- Remembers conversations across sessions
- Learns user preferences over time
- Semantic memory for contextual recall
- Character-specific memory banks

### Image Generation
- Characters can generate images to express themselves
- User can request images with natural language
- Supports multiple art styles (realistic, anime, artistic)
- Safe generation with user-controlled content filters

### Internet Access
- Characters can search for current information
- Real-time fact checking
- News updates and current events
- Optional feature (can be disabled)

## Configuration

### Environment Variables
```env
# LLM Settings
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=dolphin-mistral:7b-v2.8-q4_K_M
LLM_TEMPERATURE=0.8
LLM_MAX_TOKENS=2048

# Stable Diffusion Settings
SD_API_URL=http://localhost:7860
SD_MODEL=sd_xl_base_1.0.safetensors
SD_STEPS=30
SD_CFG_SCALE=7.0

# Memory Settings
MEMORY_ENABLED=true
VECTOR_DB_PATH=./data/chromadb

# Search Settings
ENABLE_WEB_SEARCH=true
SEARCH_PROVIDER=duckduckgo

# Server Settings
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

## Character Presets

### 1. Virtual Girlfriend
Romantic, caring, playful personality with emotional intelligence.

### 2. Therapist (Dr. Sarah)
Professional, empathetic, trained in cognitive behavioral therapy techniques.

### 3. Best Friend
Casual, supportive, shares interests and hobbies.

### 4. Creative Muse
Artistic, imaginative, helps with creative projects.

## Privacy & Security

- **100% Local Processing**: All AI processing happens on your device
- **No Data Collection**: Zero telemetry or analytics
- **No Internet Required**: Except for optional web search feature
- **No API Keys**: No paid services or external dependencies
- **Encrypted Storage**: Local database encryption option

## Performance Optimization

### For RTX 4060 (8GB VRAM)
- Use 4-bit quantized models (Q4_K_M)
- Recommended: 7B-12B parameter models
- SD XL with xformers optimization
- Batch size 1 for image generation

### Memory Management
- Conversation history: Last 50 messages
- Vector memory: Top 10 relevant memories
- Image cache: Last 20 images

## Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues.

### GPU Not Detected
- Verify NVIDIA drivers installed
- Check CUDA installation: `nvidia-smi`
- Reinstall PyTorch with CUDA support

### Out of Memory Errors
- Use smaller quantization (Q4 instead of Q5)
- Reduce max_tokens in config
- Close other GPU applications

### Slow Generation
- Switch to smaller model
- Enable xformers for SD
- Reduce SD steps to 20-25

## Legal & Ethical Use

This software is provided for:
- Personal use and entertainment
- Mental health support (not replacement for professional help)
- Creative and artistic exploration
- Research and education

**Important Notes:**
- Not a replacement for real human relationships
- Therapist character is not a licensed professional
- Use responsibly and ethically
- Respect local laws and regulations

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## License

MIT License - See LICENSE file

## Acknowledgments

- Ollama team for easy LLM deployment
- Automatic1111 for Stable Diffusion WebUI
- Eric Hartford for Dolphin models
- Civitai community for models and LoRAs
- Open source AI community

## Support

For issues and questions:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review [GitHub Issues](issues)
3. Consult [User Guide](docs/USER_GUIDE.md)

## Roadmap

- [ ] Voice chat with TTS/STT
- [ ] Video generation (AnimateDiff)
- [ ] Multi-modal chat (send images)
- [ ] Character sharing/import
- [ ] Mobile app (Android)
- [ ] VR integration
- [ ] Multiple language support

---

**Note**: This is a personal project for running on your own hardware. No cloud services, subscriptions, or data sharing involved.
