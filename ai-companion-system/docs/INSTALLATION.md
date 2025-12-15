# Installation Guide

Complete step-by-step installation guide for AI Companion System on Windows 11 with RTX 4060 GPU.

## Prerequisites

### System Requirements
- **OS**: Windows 11
- **GPU**: NVIDIA RTX 4060 (8GB VRAM) or better
- **RAM**: 16GB minimum
- **Storage**: 50GB free space
- **CPU**: Intel i7 or AMD Ryzen 7

### Software Requirements
- **Python**: 3.10 or 3.11 ([Download](https://www.python.org/downloads/))
- **Node.js**: 18+ ([Download](https://nodejs.org/))
- **Git**: Latest version ([Download](https://git-scm.com/))
- **NVIDIA Drivers**: Latest ([Download](https://www.nvidia.com/download/index.aspx))
- **CUDA**: 11.8 or 12.1 (included with drivers)

## Step 1: Clone Repository

```bash
git clone <your-repository-url>
cd ai-companion-system
```

## Step 2: Run Automated Setup (Recommended)

Open PowerShell as Administrator and run:

```powershell
cd ai-companion-system
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup_windows.ps1
```

This will:
- Check system requirements
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies

## Step 3: Install Ollama

1. Download Ollama from [https://ollama.ai/download](https://ollama.ai/download)
2. Install Ollama
3. Open a new terminal and verify: `ollama --version`

## Step 4: Download LLM Models

Run the model downloader script:

```bash
python scripts/download_models.py
```

Or manually:

```bash
# Recommended for RTX 4060
ollama pull dolphin-mistral:7b-v2.8

# Alternative (requires more VRAM)
ollama pull dolphin2.9-mistral-nemo:12b
```

Verify model is downloaded:
```bash
ollama list
```

## Step 5: Setup Stable Diffusion XL

### Install Automatic1111 WebUI

1. Clone the repository:
```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git sd-webui
cd sd-webui
```

2. Download Stable Diffusion XL Base 1.0:
   - Visit: [HuggingFace SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)
   - Download `sd_xl_base_1.0.safetensors`
   - Place in: `sd-webui/models/Stable-diffusion/`

3. Download VAE (Optional but recommended):
   - Download `sdxl_vae.safetensors`
   - Place in: `sd-webui/models/VAE/`

4. (Optional) Download LoRAs for enhanced image generation:
   - Visit: [Civitai](https://civitai.com)
   - Search for SDXL LoRAs (realistic, anime, etc.)
   - Place in: `sd-webui/models/Lora/`

5. Configure WebUI for API access:
   - Edit `webui-user.bat`
   - Add to `COMMANDLINE_ARGS`: `--api --xformers --no-half-vae`
   - Example: `set COMMANDLINE_ARGS=--api --xformers --no-half-vae`

6. Launch WebUI:
```bash
webui-user.bat
```

7. Verify WebUI is running at: `http://127.0.0.1:7860`

## Step 6: Configure Environment

Create `.env` file in the root directory (copy from `.env.example` if provided):

```env
# LLM Settings
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=dolphin-mistral:7b-v2.8
LLM_TEMPERATURE=0.8
LLM_MAX_TOKENS=2048

# Stable Diffusion Settings
SD_API_URL=http://127.0.0.1:7860
SD_ENABLED=true
SD_MODEL=sd_xl_base_1.0.safetensors
SD_STEPS=30
SD_CFG_SCALE=7.0

# Memory Settings
MEMORY_ENABLED=true
VECTOR_DB_PATH=./data/chromadb

# Web Search
ENABLE_WEB_SEARCH=true
SEARCH_PROVIDER=duckduckgo
```

## Step 7: Initialize Database

```bash
cd backend
.\venv\Scripts\activate
python database/db.py
```

## Step 8: Start the System

### Terminal 1: Backend
```bash
cd backend
.\venv\Scripts\activate
python -m api.main
```

Or use the batch script:
```bash
.\scripts\start_backend.bat
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Or use the batch script:
```bash
.\scripts\start_frontend.bat
```

### Terminal 3: Ollama (if not running as service)
```bash
ollama serve
```

### Terminal 4: Stable Diffusion WebUI
```bash
cd sd-webui
webui-user.bat
```

## Step 9: Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## Verification

1. **Check Backend**: `http://localhost:8000/health`
2. **Check LLM**: Should show "ok" in health endpoint
3. **Check SD**: Should show "ok" in health endpoint
4. **Create Test Character**: Use the Characters tab
5. **Send Test Message**: Try chatting with the character
6. **Generate Test Image**: Use the Gallery tab

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Next Steps

1. Create your first AI character
2. Customize character appearance for image generation
3. Start chatting and generating images
4. Explore memory features
5. Check out [USER_GUIDE.md](USER_GUIDE.md) for feature details

## Performance Optimization

For RTX 4060 (8GB VRAM):

1. **LLM**: Use 4-bit quantized models (Q4_K_M)
2. **SDXL**: Use `--xformers` flag for memory optimization
3. **Steps**: Start with 20-25 steps, increase if quality isn't good enough
4. **Resolution**: 1024x1024 is optimal for SDXL
5. **Batch Size**: Keep at 1 for RTX 4060

## Updates

To update the system:

```bash
git pull
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt

cd ../frontend
npm install
```

## Uninstallation

To remove the system:

1. Delete the project folder
2. Uninstall Ollama (optional)
3. Delete SD WebUI folder (optional)
4. Remove Python virtual environment
