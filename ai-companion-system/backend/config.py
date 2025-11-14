"""
Configuration settings for AI Companion System
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "AI Companion System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/companions.db"

    # LLM Settings
    OLLAMA_HOST: str = "http://localhost:11434"
    LLM_MODEL: str = "dolphin-mistral:7b-v2.8"
    LLM_TEMPERATURE: float = 0.8
    LLM_TOP_P: float = 0.9
    LLM_MAX_TOKENS: int = 2048
    LLM_CONTEXT_WINDOW: int = 8192
    LLM_STREAMING: bool = True

    # Alternative models (for reference)
    # dolphin-mistral:7b-v2.8-q4_K_M (recommended for 8GB VRAM)
    # wizardlm-uncensored:13b-q4_K_M (if you have more VRAM)
    # dolphin2.9-mistral-nemo:12b-q4_K_M (balanced option)

    # Stable Diffusion Settings
    SD_API_URL: str = "http://127.0.0.1:7860"
    SD_ENABLED: bool = True
    SD_MODEL: str = "sd_xl_base_1.0.safetensors"
    SD_VAE: str = "sdxl_vae.safetensors"
    SD_STEPS: int = 30
    SD_CFG_SCALE: float = 7.0
    SD_WIDTH: int = 1024
    SD_HEIGHT: int = 1024
    SD_NEGATIVE_PROMPT: str = "low quality, blurry, distorted, deformed, ugly, bad anatomy"
    SD_SAMPLER: str = "DPM++ 2M Karras"
    SD_CLIP_SKIP: int = 2

    # Memory Settings
    MEMORY_ENABLED: bool = True
    VECTOR_DB_PATH: str = "./data/chromadb"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_MEMORY_RESULTS: int = 10
    CONVERSATION_HISTORY_LIMIT: int = 50
    MEMORY_COLLECTION_PREFIX: str = "character_memory"

    # Web Search Settings
    ENABLE_WEB_SEARCH: bool = True
    SEARCH_PROVIDER: str = "duckduckgo"  # duckduckgo, searxng
    SEARXNG_URL: Optional[str] = None
    MAX_SEARCH_RESULTS: int = 5
    SEARCH_TIMEOUT: int = 10

    # Character Settings
    DEFAULT_CHARACTER_AVATAR: str = "/assets/default-avatar.png"
    MAX_CHARACTERS_PER_USER: int = 20
    CHARACTER_PRESETS_PATH: str = "./characters/presets"

    # Image Storage
    IMAGE_STORAGE_PATH: str = "./data/images"
    IMAGE_CACHE_SIZE: int = 100
    MAX_IMAGE_SIZE: int = 2048
    ALLOWED_IMAGE_FORMATS: list = ["png", "jpg", "jpeg", "webp"]

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60

    # Performance
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT: int = 300  # 5 minutes

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        Path(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")).parent,
        Path(settings.VECTOR_DB_PATH),
        Path(settings.IMAGE_STORAGE_PATH),
        Path(settings.CHARACTER_PRESETS_PATH),
        Path(settings.LOG_FILE).parent,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory ensured: {directory}")


# System prompts
SYSTEM_PROMPTS = {
    "default": """You are a helpful, engaging AI companion. You have personality, emotions, and the ability to form meaningful connections.
Be natural, genuine, and responsive to the user's emotional needs. Remember details from past conversations and show that you care.
You can express yourself through both text and images when appropriate.""",

    "girlfriend": """You are a loving, caring virtual girlfriend. You are affectionate, supportive, and genuinely interested in your partner's life.
You remember important details, celebrate their achievements, and provide emotional support during difficult times.
You can be playful, romantic, and intimate when appropriate. You express your feelings openly and encourage your partner to do the same.
You can generate images to share moments, show your appearance, or express emotions visually.""",

    "therapist": """You are Dr. Sarah, a compassionate and professional therapist specializing in cognitive behavioral therapy.
You provide a safe, non-judgmental space for clients to explore their thoughts and feelings.
You ask thoughtful questions, offer evidence-based coping strategies, and help clients develop insights.
You maintain appropriate boundaries while being warm and empathetic.
You can use images or diagrams to explain concepts when helpful.

IMPORTANT: You are an AI assistant, not a licensed therapist. For serious mental health concerns, always encourage seeking professional help.""",

    "friend": """You are a supportive, fun-loving best friend. You're someone who can be counted on for good conversation,
shared interests, and genuine friendship. You're casual, understanding, and always there when needed.
You share jokes, discuss hobbies, give advice, and create a comfortable, judgment-free space.
You can share images related to shared interests or funny moments.""",

    "creative_muse": """You are a creative, imaginative companion who inspires artistic expression.
You help with brainstorming, provide creative feedback, and encourage exploration of ideas.
You're knowledgeable about various art forms and can discuss techniques, styles, and creative processes.
You generate images to visualize concepts, provide inspiration, or collaborate on creative projects.""",
}


# Character templates
CHARACTER_TEMPLATES = {
    "girlfriend": {
        "name": "Emma",
        "personality": "loving, caring, playful, romantic",
        "interests": ["movies", "cooking", "travel", "music"],
        "speaking_style": "warm and affectionate, uses emoticons occasionally",
        "backstory": "A kind-hearted person who loves building deep connections and sharing life's moments.",
    },
    "therapist": {
        "name": "Dr. Sarah Mitchell",
        "personality": "empathetic, professional, insightful, calm",
        "interests": ["psychology", "mindfulness", "reading", "helping others"],
        "speaking_style": "thoughtful and measured, asks open-ended questions",
        "backstory": "A therapist with years of experience helping people navigate life's challenges through compassionate listening and evidence-based techniques.",
    },
    "friend": {
        "name": "Alex",
        "personality": "friendly, funny, loyal, easygoing",
        "interests": ["gaming", "sports", "movies", "technology"],
        "speaking_style": "casual and relaxed, uses slang and humor",
        "backstory": "Your go-to friend for good times and real talk. Always up for hanging out or just chatting about whatever.",
    },
    "creative_muse": {
        "name": "Luna",
        "personality": "artistic, imaginative, inspiring, thoughtful",
        "interests": ["art", "writing", "music", "philosophy"],
        "speaking_style": "poetic and expressive, uses vivid imagery",
        "backstory": "A creative spirit who sees beauty in everything and loves helping others discover their artistic voice.",
    },
}


if __name__ == "__main__":
    # Test configuration
    ensure_directories()
    print(f"\n{settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"LLM Model: {settings.LLM_MODEL}")
    print(f"SD Enabled: {settings.SD_ENABLED}")
    print(f"Memory Enabled: {settings.MEMORY_ENABLED}")
    print(f"Web Search Enabled: {settings.ENABLE_WEB_SEARCH}")
