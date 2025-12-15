# Changelog

All notable changes to the AI Companion System.

## [1.1.0] - Enhanced Web Search & News Access

### 🌐 Major Feature: Intelligent News & Web Search

Added comprehensive internet access capabilities allowing characters to discuss current events and provide up-to-date information.

#### New Features

**Backend Enhancements:**
- ✅ Automatic search detection - intelligently determines when to search
- ✅ Dual search modes:
  - Web search for general information
  - News search for current events and breaking news
- ✅ `is_news_query()` method to detect news-specific queries
- ✅ Enhanced search trigger keywords (25+ trigger phrases)
- ✅ Improved search result formatting with news-specific context
- ✅ Search metadata stored in message records
- ✅ Character-appropriate instruction in search results

**API Updates:**
- ✅ `ChatResponse` now includes `search_performed` and `search_query` fields
- ✅ Message metadata includes search information
- ✅ Automatic search type selection (web vs news)

**Frontend Enhancements:**
- ✅ Visual search indicators in chat interface
- ✅ Search icon (🔍) for web searches
- ✅ Newspaper icon (📰) for news searches
- ✅ Search query displayed in chip format
- ✅ Enhanced message metadata handling

#### Files Modified

**Backend:**
- `backend/api/routes/chat.py` - Added search metadata tracking
- `backend/api/services/search_service.py` - Added `is_news_query()`, enhanced formatting

**Frontend:**
- `frontend/src/components/ChatInterface.jsx` - Added search indicators

#### New Documentation

- `docs/WEB_SEARCH_FEATURE.md` - Comprehensive guide to web search feature
- `docs/EXAMPLE_CONVERSATIONS.md` - Real conversation examples with search
- Updated `docs/USER_GUIDE.md` - Added web search section
- Updated `README.md` - Enhanced web access description

### How It Works

1. User sends message with search trigger keywords
2. System detects if search would be helpful
3. Determines if it's a news query or general web search
4. Performs appropriate search via DuckDuckGo
5. Formats results for LLM context
6. Character responds with personality-appropriate reaction
7. Search metadata displayed in UI

### Example Usage

```
User: What's the latest news about AI?
Character: *📰 Searched: AI latest news*
Character: According to recent articles from TechCrunch and The Verge...
```

### Search Triggers

The system now recognizes 25+ search trigger phrases including:
- "What is...", "Who is...", "When did...", "Where is..."
- "What's happening", "Latest", "Current", "Recent"
- "News", "Breaking", "Headlines", "Today's"
- "Tell me about...", "Look up...", "Search for..."

### Character Personality Integration

Each character type responds to news/information differently:
- **Girlfriend**: Excited, relates to shared interests
- **Therapist**: Professional, helps process information
- **Friend**: Casual and enthusiastic
- **Creative Muse**: Finds inspiration and connections

### Privacy & Performance

- Uses DuckDuckGo (privacy-focused, no tracking)
- No API keys required
- Searches cached in local database only
- Minimal performance impact (2-5 seconds)

---

## [1.0.0] - Initial Release

### Core Features

**AI Chat:**
- Uncensored LLM integration with Ollama
- Dolphin Mistral 7B model support
- Streaming responses
- Context-aware conversations

**Image Generation:**
- Stable Diffusion XL integration
- Multiple art styles (realistic, anime, manga, artistic)
- Character-specific image generation
- Automatic prompt enhancement

**Memory System:**
- ChromaDB vector database
- Semantic memory search
- Automatic memory extraction
- Character-specific memory banks

**Character Management:**
- 4 preset characters (Girlfriend, Therapist, Friend, Creative Muse)
- Custom character creation
- Appearance descriptions for images
- Personality and backstory customization

**Web Search:**
- Basic DuckDuckGo integration
- Web search capability
- Quick answer support

**Frontend:**
- React 18 with Material-UI
- Dark theme interface
- Chat interface with history
- Character management
- Image generation gallery
- Settings panel

**Setup & Documentation:**
- Windows PowerShell setup script
- Model downloader script
- Startup batch files
- Comprehensive installation guide
- User guide
- Troubleshooting guide

### Technology Stack

- Backend: FastAPI, SQLAlchemy, asyncio
- Frontend: React 18, Material-UI, Axios
- LLM: Ollama with Dolphin Mistral
- Images: Stable Diffusion XL via Automatic1111
- Memory: ChromaDB with sentence-transformers
- Search: DuckDuckGo API
- Database: SQLite with async support

### System Requirements

- Windows 11
- NVIDIA RTX 4060 or better
- 16GB RAM minimum
- 50GB storage
- Python 3.10/3.11
- Node.js 18+

---

## Future Roadmap

### Planned Features

**v1.2.0 - Voice Integration**
- Text-to-speech (TTS) for character voices
- Speech-to-text (STT) for voice input
- Voice chat mode

**v1.3.0 - Enhanced Media**
- Video generation capabilities
- Animated images (GIFs)
- Audio generation (music, effects)

**v1.4.0 - Multi-User & Cloud**
- Multi-user support
- Character sharing/import/export
- Optional cloud sync
- Mobile companion app

**v1.5.0 - Advanced AI**
- Multiple LLM support
- Model switching per character
- Custom fine-tuning
- Emotion detection

**v2.0.0 - Platform Expansion**
- Linux support
- macOS support
- Docker deployment
- API for third-party integration

### Community Requests

We're open to community suggestions! Submit feature requests via GitHub Issues.

---

## Release Notes

### Version 1.1.0 Highlights

This release focuses on making characters truly intelligent about current events. Characters can now:

✅ Automatically search the web when needed
✅ Access and discuss latest news
✅ Provide up-to-date information
✅ React intelligently based on their personality
✅ Show search activity transparently

The implementation is seamless - users simply ask questions naturally, and characters handle the rest!

### Upgrade Instructions

If upgrading from v1.0.0:

1. Pull latest code: `git pull`
2. Update backend dependencies: `pip install -r requirements.txt`
3. Update frontend dependencies: `npm install`
4. Restart both backend and frontend
5. Test with: "What's the latest news about AI?"

No database migrations needed - fully backward compatible!

---

**Note**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
