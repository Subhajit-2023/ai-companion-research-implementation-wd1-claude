"""
FastAPI Main Application
AI Companion System Backend
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import settings, ensure_directories
from database.db import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print(f"\n{'='*50}")
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"{'='*50}\n")

    ensure_directories()
    await init_db()

    print(f"✓ LLM Model: {settings.LLM_MODEL}")
    print(f"✓ SD Enabled: {settings.SD_ENABLED}")
    print(f"✓ Memory Enabled: {settings.MEMORY_ENABLED}")
    print(f"✓ Web Search Enabled: {settings.ENABLE_WEB_SEARCH}")
    print(f"\n{'='*50}")
    print(f"Server running on http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    print(f"{'='*50}\n")

    yield

    await close_db()
    print("\n✓ Server shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

image_storage_path = Path(settings.IMAGE_STORAGE_PATH)
if image_storage_path.exists():
    app.mount("/images", StaticFiles(directory=str(image_storage_path)), name="images")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    print(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from api.services.llm_service import llm_service
    from api.services.image_service import image_service

    llm_available = llm_service.check_model_availability()
    sd_available = await image_service.check_availability() if settings.SD_ENABLED else False

    return {
        "status": "healthy",
        "llm": {
            "enabled": True,
            "available": llm_available,
            "model": settings.LLM_MODEL
        },
        "image_generation": {
            "enabled": settings.SD_ENABLED,
            "available": sd_available
        },
        "memory": {
            "enabled": settings.MEMORY_ENABLED
        },
        "search": {
            "enabled": settings.ENABLE_WEB_SEARCH
        }
    }


@app.get("/config")
async def get_config():
    """Get public configuration"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "features": {
            "image_generation": settings.SD_ENABLED,
            "memory": settings.MEMORY_ENABLED,
            "web_search": settings.ENABLE_WEB_SEARCH
        },
        "limits": {
            "max_characters": settings.MAX_CHARACTERS_PER_USER,
            "conversation_history": settings.CONVERSATION_HISTORY_LIMIT
        }
    }


from api.routes import chat, characters, images, search, memory

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
