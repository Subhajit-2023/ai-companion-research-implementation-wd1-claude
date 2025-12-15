# Complete Setup Guide - AI Companion System with Visual Novels

## System Overview

This AI Companion System includes:
- **AI Chat Companions** with customizable personalities
- **Uncensored Image Generation** using Stable Diffusion XL
- **Long-term Memory** with ChromaDB
- **Web Search & News Access** for current information
- **Visual Novel System** - Story-driven experiences with branching narratives
- **Character Management** - Create, customize, and delete characters

## Prerequisites

### Required Software

1. **Python 3.10+**
   - Download from python.org
   - Ensure `pip` is installed

2. **Node.js 18+**
   - Download from nodejs.org
   - Includes npm package manager

3. **Ollama** (for LLM)
   - Download from ollama.ai
   - Install Dolphin Mistral model:
     ```bash
     ollama pull dolphin-mistral
     ```

4. **Stable Diffusion WebUI** (for image generation)
   - Clone: `git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git`
   - Follow installation instructions
   - **IMPORTANT**: Start with `--api` flag:
     ```bash
     ./webui.sh --api  # Linux/Mac
     webui.bat --api   # Windows
     ```

## Installation Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd ai-companion-system/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and create default user
python init_db_and_user.py

# Initialize sample Visual Novel stories (optional)
python init_sample_stories.py
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 3. Configuration

The `.env` file in the backend directory contains all configuration:

```env
# Application
APP_NAME="AI Companion System"
DEBUG=true

# Backend Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/companions.db

# Ollama LLM
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=dolphin-mistral:latest

# Stable Diffusion
SD_ENABLED=true
SD_API_URL=http://127.0.0.1:7860
SD_MODEL=sd_xl_base_1.0.safetensors

# Memory System
MEMORY_ENABLED=true
CHROMA_PERSIST_DIR=./data/chroma

# Web Search
ENABLE_WEB_SEARCH=true
SEARCH_PROVIDER=duckduckgo
MAX_SEARCH_RESULTS=5
```

## Running the System

### Start All Services

You need 3 services running:

#### 1. Ollama (Terminal 1)
```bash
# Should already be running in background
# If not:
ollama serve
```

#### 2. Stable Diffusion WebUI (Terminal 2)
```bash
cd path/to/stable-diffusion-webui
./webui.sh --api  # or webui.bat --api on Windows
```

#### 3. Backend API (Terminal 3)
```bash
cd ai-companion-system/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python api/main.py
```

#### 4. Frontend (Terminal 4) - For Development
```bash
cd ai-companion-system/frontend
npm run dev
```

**For production**: The backend serves the built frontend automatically at `http://localhost:8000`

### Access the Application

Open your browser and go to:
- **Development**: `http://localhost:5173`
- **Production**: `http://localhost:8000`

## Feature Guide

### 1. Chat with AI Companions

- Click **Chat** in sidebar
- Select a character or create a new one
- Start chatting!
- Characters can:
  - Search the web for current information
  - Access latest news
  - Generate images based on conversation
  - Remember past conversations

### 2. Character Management

- Click **Characters** in sidebar
- **Create New Character**:
  - Choose a persona type (girlfriend, therapist, friend, custom)
  - Customize personality, interests, speaking style
  - Add appearance description for image generation
- **Delete Character**: Click red trash icon
- Pre-loaded personas:
  - **Luna** - Girlfriend
  - **Dr. Sarah** - Therapist
  - **Alex** - Friend
  - **Aria** - Creative Muse

### 3. Image Generation

- Click **Gallery** in sidebar
- Enter a prompt describing what you want
- Choose art style: realistic, anime, manga, artistic
- Adjust quality settings
- Click **Generate**
- Images appear in gallery and can be shared in chat

### 4. Visual Novel System

The star feature! Story-driven experiences with:

#### Playing Visual Novels

1. Click **Visual Novels** in sidebar
2. Browse available stories
3. Click **Start New Game**
4. Experience the story:
   - Read narrative text
   - Listen to character dialogue
   - Make choices that matter
   - Generate scene backgrounds and character sprites
   - Reach different endings based on your decisions

#### Sample Story: "Echoes of Time"

A mystery thriller inspired by Steins;Gate:
- **Genre**: Mystery, Sci-Fi, Thriller
- **Playtime**: ~30 minutes
- **Endings**: 3 different endings
- **Choices**: 2 major choice points
- **Theme**: Time loops and difficult decisions

**Synopsis**: You discover a device that can send messages to the past. Your friend is in danger, and you must use time loops to save them.

#### Visual Novel Features

- **Branching Narratives** - Your choices change the story
- **Multiple Endings** - Discover all possible outcomes
- **Save/Load System** - Continue where you left off
- **AI-Generated Imagery** - Generate backgrounds and character sprites
- **Professional UI** - Visual novel-style text boxes and presentation
- **Choice Tracking** - See the consequences of your decisions

### 5. Web Search & News

Characters can access the internet:

**Trigger Web Search**:
- "What is [topic]?"
- "Search for [query]"
- "Look up [information]"

**Trigger News Search**:
- "What's the latest news about [topic]?"
- "Tell me today's headlines"
- "What's happening in [location]?"

Characters will search and discuss results naturally based on their personality.

## Troubleshooting

### Images Not Generating

**Problem**: "Image generation failed" error

**Solutions**:
1. Verify SD WebUI is running: `http://127.0.0.1:7860`
2. Check WebUI started with `--api` flag
3. Verify model is loaded in WebUI
4. Check backend health endpoint: `http://localhost:8000/health`

### LLM Not Responding

**Problem**: Chat responses fail or timeout

**Solutions**:
1. Check Ollama is running: `ollama list`
2. Verify model is downloaded: `ollama pull dolphin-mistral`
3. Check Ollama API: `curl http://localhost:11434/api/tags`
4. Restart Ollama service

### Visual Novel Won't Start

**Problem**: Visual novels don't load or start

**Solutions**:
1. Run story initialization:
   ```bash
   cd backend
   python init_sample_stories.py
   ```
2. Check database was initialized:
   ```bash
   python init_db_and_user.py
   ```
3. Verify backend is running
4. Check browser console for errors (F12)

### Database Errors

**Problem**: "Database locked" or "Table doesn't exist"

**Solutions**:
1. Stop all running instances
2. Delete `data/companions.db`
3. Re-run `python init_db_and_user.py`
4. Re-run `python init_sample_stories.py`
5. Restart backend

### Memory/ChromaDB Issues

**Problem**: Memory system errors

**Solutions**:
1. Delete `data/chroma` directory
2. Restart backend (will recreate ChromaDB)
3. Check sufficient disk space
4. Verify sentence-transformers model downloaded

## Creating Custom Visual Novels

### Story Structure

Visual novels consist of:
1. **Narrative Scenes** - Story progression, click to continue
2. **Choice Scenes** - Player makes decisions
3. **Ending Scenes** - Story conclusions

### Creating a Story via API

Use the VN API endpoints:

```python
# Example: Create a simple romance VN
import requests

API_BASE = "http://localhost:8000/api/vn"

# 1. Create the visual novel
novel_data = {
    "title": "My Love Story",
    "description": "A heartwarming romance...",
    "genre": "Romance, Drama",
    "total_scenes": 5,
    "estimated_playtime": 15
}

# 2. Create scenes with the API
# (See full documentation in VISUAL_NOVEL_FEATURE.md)
```

### Image Prompts

For best results:

**Background Prompts**:
```
"anime style cherry blossom park, spring day, beautiful scenery, detailed background art, soft lighting"
"dark mysterious laboratory, sci-fi setting, glowing monitors, anime background, dramatic atmosphere"
```

**Character Prompts**:
```
"anime girl with long dark hair, school uniform, happy expression, full body, detailed anime art"
"male protagonist in casual clothes, determined look, character sprite, standing pose, anime style"
```

## API Documentation

### Visual Novel Endpoints

```
GET  /api/vn/novels              - List all visual novels
GET  /api/vn/novels/{id}         - Get specific novel
POST /api/vn/sessions/start      - Start new playthrough
GET  /api/vn/sessions/{id}       - Get session state
POST /api/vn/sessions/{id}/advance - Advance to next scene
POST /api/vn/sessions/{id}/choice  - Make a choice
POST /api/vn/scenes/{id}/generate-image - Generate scene image
GET  /api/vn/scenes/{id}/assets  - Get scene assets
```

### Other Endpoints

```
POST /api/chat/send              - Send chat message
GET  /api/characters/            - List characters
POST /api/characters/            - Create character
DELETE /api/characters/{id}      - Delete character
POST /api/images/generate        - Generate image
GET  /api/images/                - List generated images
```

Full API docs: `http://localhost:8000/docs` (when backend is running)

## System Architecture

```
AI Companion System
├── Backend (FastAPI + Python)
│   ├── LLM Service (Ollama)
│   ├── Image Service (Stable Diffusion)
│   ├── Memory Service (ChromaDB)
│   ├── Search Service (DuckDuckGo)
│   ├── Character System
│   ├── Visual Novel Engine
│   └── Database (SQLite)
│
└── Frontend (React + Vite)
    ├── Chat Interface
    ├── Character Manager
    ├── Image Gallery
    ├── Visual Novel Player
    └── Settings
```

## Performance Tips

1. **Image Generation**: Takes 3-10 seconds depending on hardware
2. **LLM Responses**: Typically 1-3 seconds with Dolphin Mistral
3. **Memory Retrieval**: Nearly instant with ChromaDB
4. **Web Search**: 1-2 seconds for results

### Optimization

- **GPU**: Use NVIDIA GPU for SD (MUCH faster)
- **RAM**: 16GB+ recommended for smooth operation
- **Storage**: Keep 10GB+ free for generated images
- **CPU**: Multi-core recommended for simultaneous services

## Security Notes

- Default setup is for **local use only**
- Do NOT expose backend to internet without authentication
- Image generation is **uncensored** - use responsibly
- Keep Ollama and SD WebUI on localhost
- Character data stored locally in SQLite

## Updates and Maintenance

### Backing Up Data

Important directories to backup:
```
backend/data/companions.db      # All characters, messages, saves
backend/data/chroma/            # Memory embeddings
backend/data/images/            # Generated images
```

### Updating Models

**Update Ollama Model**:
```bash
ollama pull dolphin-mistral:latest
```

**Update SD Model**:
- Download new model to `stable-diffusion-webui/models/Stable-diffusion/`
- Update `SD_MODEL` in `.env`
- Restart SD WebUI

## Next Steps

1. **Create Your First Character**
   - Go to Characters tab
   - Click "Create New Character"
   - Customize personality and appearance

2. **Play the Sample Visual Novel**
   - Go to Visual Novels tab
   - Start "Echoes of Time"
   - Experience the branching story

3. **Generate Custom Images**
   - Go to Gallery tab
   - Try different prompts and styles
   - Use generated images in chat

4. **Explore Web Search**
   - Ask your character about current events
   - Request latest news on topics
   - See intelligent responses based on real data

## Support and Resources

- **Backend Logs**: Check terminal output for errors
- **Frontend Console**: Press F12 in browser
- **Health Check**: `http://localhost:8000/health`
- **API Docs**: `http://localhost:8000/docs`

## License

See LICENSE file in project root.

---

**Enjoy your AI companions and visual novel adventures!** 🎭✨
