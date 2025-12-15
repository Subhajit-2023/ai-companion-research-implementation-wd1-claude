# Quick Reference Guide

## Start-Up Commands

### 1. Start Ollama (if not running)
```bash
ollama serve
```

### 2. Start Stable Diffusion WebUI
```bash
cd path/to/stable-diffusion-webui
./webui.sh --api  # Linux/Mac
webui.bat --api   # Windows
```

### 3. Start Backend
```bash
cd ai-companion-system/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python api/main.py
```

### 4. Start Frontend (Development)
```bash
cd ai-companion-system/frontend
npm run dev
```

**Or for production**: Backend serves frontend at `http://localhost:8000`

---

## First-Time Setup

### 1. Install Dependencies

**Backend**:
```bash
cd ai-companion-system/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend**:
```bash
cd ai-companion-system/frontend
npm install
npm run build
```

### 2. Download Models
```bash
ollama pull dolphin-mistral
```

### 3. Initialize Database
```bash
cd backend
python init_db_and_user.py
python init_sample_stories.py  # For Visual Novel sample
```

---

## API Endpoints

### Chat
- `POST /api/chat/send` - Send message
- `GET /api/chat/history/{character_id}` - Get history

### Characters
- `GET /api/characters/` - List all
- `POST /api/characters/` - Create new
- `GET /api/characters/{id}` - Get specific
- `PUT /api/characters/{id}` - Update
- `DELETE /api/characters/{id}` - Delete

### Images
- `POST /api/images/generate` - Generate image
- `GET /api/images/` - List all
- `GET /api/images/{id}` - Get specific

### Visual Novels
- `GET /api/vn/novels` - List novels
- `POST /api/vn/sessions/start` - Start game
- `POST /api/vn/sessions/{id}/advance` - Next scene
- `POST /api/vn/sessions/{id}/choice` - Make choice
- `POST /api/vn/scenes/{id}/generate-image` - Generate scene image

### Search
- `POST /api/search/web` - Web search
- `POST /api/search/news` - News search

---

## URLs

### When Running

- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Frontend (dev)**: `http://localhost:5173`
- **Frontend (prod)**: `http://localhost:8000`
- **Ollama**: `http://localhost:11434`
- **SD WebUI**: `http://localhost:7860`

---

## File Locations

### Data Storage
- **Database**: `backend/data/companions.db`
- **Generated Images**: `backend/data/images/`
- **ChromaDB**: `backend/data/chroma/`

### Configuration
- **Backend Config**: `backend/.env`
- **Character Presets**: `backend/characters/presets/`

### Logs
- Check terminal output where backend is running

---

## Common Commands

### Backend

**Activate virtual environment**:
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Run backend**:
```bash
python api/main.py
# or
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Initialize database**:
```bash
python init_db_and_user.py
```

**Create sample VN stories**:
```bash
python init_sample_stories.py
```

### Frontend

**Install dependencies**:
```bash
npm install
```

**Development mode**:
```bash
npm run dev
```

**Build for production**:
```bash
npm run build
```

**Preview production build**:
```bash
npm run preview
```

### Ollama

**List models**:
```bash
ollama list
```

**Pull model**:
```bash
ollama pull dolphin-mistral
```

**Run model**:
```bash
ollama run dolphin-mistral
```

---

## Troubleshooting Quick Fixes

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process if needed
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Images not generating
1. Check SD WebUI is running: `http://localhost:7860`
2. Verify `--api` flag was used when starting
3. Check health endpoint: `http://localhost:8000/health`

### LLM not responding
1. Check Ollama is running: `ollama list`
2. Verify model downloaded: `ollama pull dolphin-mistral`
3. Test Ollama: `curl http://localhost:11434/api/tags`

### Database locked
1. Stop all backend instances
2. Delete `backend/data/companions.db`
3. Run `python init_db_and_user.py`
4. Run `python init_sample_stories.py`

### Frontend build fails
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install`
3. Run `npm run build`

---

## Environment Variables (.env)

### Required Settings
```env
# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/companions.db

# LLM
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=dolphin-mistral:latest

# Stable Diffusion
SD_ENABLED=true
SD_API_URL=http://127.0.0.1:7860

# Memory
MEMORY_ENABLED=true
CHROMA_PERSIST_DIR=./data/chroma

# Search
ENABLE_WEB_SEARCH=true
```

---

## Feature Keyboard Shortcuts

### In Chat Interface
- `Enter` - Send message (when not shift+enter)
- `Shift+Enter` - New line
- `Ctrl+K` - Clear chat (if implemented)

### General
- `F12` - Open browser developer console
- `Ctrl+R` - Refresh page
- `Ctrl+Shift+R` - Hard refresh (clear cache)

---

## Default Credentials

### Default User
- **Username**: `default_user`
- **User ID**: `1`

(Authentication not implemented - single user system)

---

## Character Presets

### Available Characters

1. **Luna** (girlfriend.json)
   - Persona: girlfriend
   - Personality: Warm, caring, romantic

2. **Dr. Sarah** (therapist.json)
   - Persona: therapist
   - Personality: Professional, empathetic

3. **Alex** (friend.json)
   - Persona: friend
   - Personality: Casual, supportive

4. **Aria** (creative_muse.json)
   - Persona: creative_muse
   - Personality: Artistic, imaginative

---

## Visual Novel Sample Story

### "Echoes of Time"

**Access**: Visual Novels tab → Start New Game

**Details**:
- **Genre**: Mystery, Sci-Fi, Thriller
- **Playtime**: ~30 minutes
- **Scenes**: 8 total
- **Choice Points**: 2 major decisions
- **Endings**: 3 different outcomes
  - Too Late (Bad Ending)
  - Power of Trust (Good Ending)
  - Timeline Restored (True Ending)

**Tips**:
- Generate backgrounds and character sprites for immersion
- Your choices matter - explore different paths
- Multiple playthroughs unlock all endings

---

## Performance Tips

### Optimize for RTX 4060

**LLM Settings**:
- Use Q4 quantized models
- Max tokens: 2048
- Temperature: 0.7-0.9

**Image Generation**:
- Steps: 20-30
- Resolution: 1024x1024
- Enable xformers in SD WebUI
- Batch size: 1

**Memory**:
- Keep conversation history: last 50 messages
- Vector memory: top 10 results
- Image cache: last 20 images

---

## Backup Important Data

### What to Backup

```bash
# Database (all characters, messages, saves)
backend/data/companions.db

# Memory embeddings
backend/data/chroma/

# Generated images
backend/data/images/

# Configuration
backend/.env
```

### Backup Command
```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Copy important files
cp backend/data/companions.db backups/$(date +%Y%m%d)/
cp -r backend/data/chroma backups/$(date +%Y%m%d)/
cp -r backend/data/images backups/$(date +%Y%m%d)/
```

---

## Health Check Checklist

✅ **Before Starting Session**:
1. Ollama running: `ollama list`
2. SD WebUI running: visit `http://localhost:7860`
3. Backend running: visit `http://localhost:8000/health`
4. Frontend accessible: visit frontend URL
5. Database exists: check `backend/data/companions.db`

✅ **During Session**:
1. Check backend terminal for errors
2. Check browser console (F12) for frontend errors
3. Monitor GPU usage (if performance issues)

---

## Getting Help

### Resources
1. **SETUP_GUIDE.md** - Complete setup instructions
2. **TROUBLESHOOTING.md** - Common problems and solutions
3. **FEATURES_SUMMARY.md** - Feature documentation
4. **API Docs** - `http://localhost:8000/docs`

### Debug Steps
1. Check health endpoint
2. Review terminal logs
3. Check browser console
4. Verify all services running
5. Test individual components

---

**Quick tip**: Bookmark `http://localhost:8000/docs` for interactive API testing!
