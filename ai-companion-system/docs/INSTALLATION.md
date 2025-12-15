# Installation Guide

Complete installation guide for AI Companion System on Windows 11 with RTX 4060 GPU.

## Prerequisites

### Required Software
- **Windows 11** (64-bit)
- **Python 3.10 or 3.11** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **NVIDIA GPU Drivers** (Latest from [NVIDIA](https://www.nvidia.com/download/index.aspx))
- **CUDA 11.8 or 12.1** ([Download](https://developer.nvidia.com/cuda-downloads))

### Hardware Requirements
- **GPU**: NVIDIA RTX 4060 (8GB VRAM) or better
- **RAM**: 16GB minimum
- **Storage**: 50GB free space
- **CPU**: Intel i7 or AMD Ryzen 7

## Step 1: Install Ollama

1. Download Ollama for Windows from [https://ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open Command Prompt and verify installation:
   ```cmd
   ollama --version
   ```

4. Pull the recommended LLM model:
   ```cmd
   ollama pull dolphin-mistral:7b-v2.8
   ```

   Alternative models (if you have more VRAM):
   ```cmd
   ollama pull wizardlm-uncensored:13b
   ollama pull dolphin2.9-mistral-nemo:12b
   ```

## Step 2: Install Stable Diffusion WebUI

1. Clone the Automatic1111 WebUI repository:
   ```cmd
   git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
   cd stable-diffusion-webui
   ```

2. Download SDXL model:
   - Download `sd_xl_base_1.0.safetensors` from [Hugging Face](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)
   - Place it in `stable-diffusion-webui/models/Stable-diffusion/`

3. (Optional) Download additional models/LoRAs from [Civitai](https://civitai.com/)

4. Edit `webui-user.bat` and add `--api` flag:
   ```bat
   set COMMANDLINE_ARGS=--api --xformers
   ```

5. Run the WebUI:
   ```cmd
   webui-user.bat
   ```

6. Wait for it to start (first time takes longer)
7. Access at `http://localhost:7860`

## Step 3: Setup AI Companion System

1. Clone this repository:
   ```cmd
   git clone <repository-url>
   cd ai-companion-system
   ```

2. Create Python virtual environment:
   ```cmd
   cd backend
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

4. Create .env file (optional - uses defaults):
   ```cmd
   copy .env.example .env
   ```

5. Initialize database:
   ```cmd
   python database/db.py
   ```

## Step 4: Setup Frontend

1. Open a new terminal and navigate to frontend:
   ```cmd
   cd frontend
   ```

2. Install Node dependencies:
   ```cmd
   npm install
   ```

## Step 5: Run the Application

You'll need **3 terminal windows**:

### Terminal 1: Stable Diffusion WebUI
```cmd
cd stable-diffusion-webui
webui-user.bat
```
Wait until you see "Running on local URL: http://127.0.0.1:7860"

### Terminal 2: Backend API
```cmd
cd ai-companion-system/backend
venv\Scripts\activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
Wait until you see "Application startup complete"

### Terminal 3: Frontend
```cmd
cd ai-companion-system/frontend
npm run dev
```
Wait until you see "Local: http://localhost:5173/"

## Step 6: Access the Application

Open your browser and go to: **http://localhost:5173**

## Verification

1. Click "New Character" and create a character from template
2. Start chatting - responses should stream in real-time
3. Go to Gallery tab and generate an image
4. Verify image appears in the gallery

## Common Issues

### Ollama Not Found
- Make sure Ollama is installed and in your PATH
- Restart terminal after installation

### SD WebUI Not Starting
- Check if port 7860 is already in use
- Make sure you have enough VRAM (close other GPU applications)
- Verify CUDA is properly installed: `nvidia-smi`

### Backend Errors
- Make sure all dependencies are installed
- Check if ports 8000 is available
- Verify Python version: `python --version` (should be 3.10 or 3.11)

### Frontend Not Loading
- Make sure Node.js is installed: `node --version`
- Check if port 5173 is available
- Try `npm install` again if packages are missing

## Performance Tips

### For 8GB VRAM (RTX 4060):
- Use 4-bit quantized models (Q4_K_M)
- Keep SD steps at 20-30
- Close other GPU applications while using

### Memory Management:
- The system automatically manages conversation history
- Images are cached locally
- Old images can be deleted from Gallery tab

## Next Steps

- Read [USER_GUIDE.md](USER_GUIDE.md) for feature documentation
- See [MODELS_SETUP.md](MODELS_SETUP.md) for advanced model configuration
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## Stopping the Application

1. Press `Ctrl+C` in each terminal to stop services
2. Close Stable Diffusion WebUI window
3. All data is saved automatically
