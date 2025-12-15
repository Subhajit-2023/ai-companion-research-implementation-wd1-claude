"""
FastAPI Main Application for AI Companion System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

sys.path.append(str(Path(__file__).parent.parent))
from config import settings, ensure_directories
from database.db import init_db, close_db


logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    ensure_directories()

    await init_db()
    logger.info("Database initialized")

    from api.services.llm_service import llm_service
    if llm_service.check_model_availability():
        logger.info(f"LLM model {settings.LLM_MODEL} is available")
    else:
        logger.warning(f"LLM model {settings.LLM_MODEL} not found. Available models: {llm_service.list_available_models()}")

    from api.services.image_service import image_service
    api_available = await image_service.check_api_status()
    if api_available:
        logger.info("Stable Diffusion API is available")
    else:
        logger.warning("Stable Diffusion API is not available. Image generation will be disabled.")

    logger.info("Application started successfully")

    yield

    await close_db()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Companion System with uncensored chat and image generation",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from api.services.llm_service import llm_service
    from api.services.image_service import image_service

    llm_available = llm_service.check_model_availability()
    sd_available = await image_service.check_api_status()

    return {
        "status": "healthy",
        "services": {
            "database": "ok",
            "llm": "ok" if llm_available else "unavailable",
            "image_generation": "ok" if sd_available else "unavailable",
            "memory": "ok",
            "search": "ok" if settings.ENABLE_WEB_SEARCH else "disabled",
        },
    }


@app.get("/config")
async def get_config():
    """Get public configuration"""
    return {
        "llm_model": settings.LLM_MODEL,
        "sd_enabled": settings.SD_ENABLED,
        "memory_enabled": settings.MEMORY_ENABLED,
        "search_enabled": settings.ENABLE_WEB_SEARCH,
        "max_characters_per_user": settings.MAX_CHARACTERS_PER_USER,
    }


from pathlib import Path
image_storage = Path(settings.IMAGE_STORAGE_PATH)
if image_storage.exists():
    app.mount("/images", StaticFiles(directory=str(image_storage)), name="images")


from api.routes import chat, characters, images, visual_novel

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(visual_novel.router, prefix="/api/vn", tags=["visual-novel"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
