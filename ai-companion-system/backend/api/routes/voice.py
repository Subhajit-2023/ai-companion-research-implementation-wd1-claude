"""
Voice API Routes
Handles TTS (text-to-speech) and STT (speech-to-text) functionality
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from database.db import get_db
from api.models import Character
from api.services.tts_service import tts_service
from api.services.stt_service import stt_service

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    character_id: Optional[int] = None
    speed: float = 1.0


class TTSResponse(BaseModel):
    audio_url: str
    voice_id: str
    text: str
    cached: bool


class VoiceInfo(BaseModel):
    voice_id: str
    name: str
    gender: str
    language: str
    quality: str
    description: str
    installed: bool


class STTResponse(BaseModel):
    text: str
    language: str
    language_probability: float
    duration: float


class CharacterVoiceUpdate(BaseModel):
    voice_id: str
    voice_enabled: bool = True
    voice_speed: float = 1.0


# TTS Endpoints

@router.post("/tts/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech

    - **text**: Text to convert to speech
    - **voice_id**: Optional voice ID (uses default if not specified)
    - **character_id**: Optional character ID for caching
    - **speed**: Speech speed (0.5 to 2.0, default 1.0)
    """
    if not request.text or len(request.text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if request.speed < 0.5 or request.speed > 2.0:
        raise HTTPException(status_code=400, detail="Speed must be between 0.5 and 2.0")

    result = await tts_service.synthesize_speech(
        text=request.text,
        voice_id=request.voice_id,
        character_id=request.character_id,
        speed=request.speed
    )

    if not result:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate speech. Ensure Piper TTS is installed and voice models are downloaded."
        )

    return TTSResponse(**result)


@router.get("/tts/voices", response_model=List[VoiceInfo])
async def get_available_voices():
    """
    Get list of available TTS voices

    Returns voice metadata including which voices are installed
    """
    voices = tts_service.get_available_voices()

    voice_list = []
    for voice_id, info in voices.items():
        voice_list.append(VoiceInfo(voice_id=voice_id, **info))

    return voice_list


@router.get("/tts/voices/downloaded")
async def get_downloaded_voices():
    """Get list of downloaded voice models"""
    models = tts_service.list_downloaded_models()
    return {"voices": models, "count": len(models)}


@router.get("/tts/check")
async def check_tts_availability():
    """Check if TTS service is available"""
    piper_available = tts_service.check_piper_installed()
    downloaded_models = tts_service.list_downloaded_models()

    return {
        "piper_installed": piper_available,
        "models_downloaded": len(downloaded_models),
        "available": piper_available and len(downloaded_models) > 0,
        "models": downloaded_models
    }


# STT Endpoints

@router.post("/stt/transcribe", response_model=STTResponse)
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form("en")
):
    """
    Transcribe audio to text

    - **audio**: Audio file (wav, mp3, ogg, etc.)
    - **language**: Language code (en, es, fr, etc.) or None for auto-detect
    """
    # Validate file
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Read audio data
    audio_bytes = await audio.read()

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # Transcribe
    result = await stt_service.transcribe_audio_bytes(
        audio_bytes=audio_bytes,
        filename=audio.filename,
        language=language if language else None
    )

    if not result:
        raise HTTPException(
            status_code=500,
            detail="Failed to transcribe audio. Ensure Whisper model is installed."
        )

    return STTResponse(
        text=result["text"],
        language=result["language"],
        language_probability=result["language_probability"],
        duration=result["duration"]
    )


@router.get("/stt/models")
async def get_stt_models():
    """Get information about available Whisper models"""
    models = stt_service.get_available_models()
    current = stt_service.get_model_info()

    return {
        "available_models": models,
        "current_model": current
    }


@router.post("/stt/model/change")
async def change_stt_model(model_size: str):
    """Change Whisper model size"""
    success = stt_service.change_model(model_size)

    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load model: {model_size}"
        )

    return {
        "success": True,
        "model": model_size,
        "info": stt_service.get_model_info()
    }


@router.get("/stt/check")
async def check_stt_availability():
    """Check if STT service is available"""
    model_loaded = stt_service.is_model_loaded()

    if not model_loaded:
        # Try to load
        model_loaded = stt_service.load_model()

    return {
        "available": model_loaded,
        "model_info": stt_service.get_model_info()
    }


# Character Voice Settings

@router.put("/characters/{character_id}/voice")
async def update_character_voice(
    character_id: int,
    voice_settings: CharacterVoiceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update voice settings for a character

    - **character_id**: Character ID
    - **voice_id**: Voice model to use
    - **voice_enabled**: Enable/disable voice for character
    - **voice_speed**: Speech speed (0.5 to 2.0)
    """
    # Get character
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Validate voice exists
    available_voices = tts_service.get_available_voices()
    if voice_settings.voice_id not in available_voices:
        raise HTTPException(
            status_code=400,
            detail=f"Voice ID '{voice_settings.voice_id}' not found"
        )

    # Update voice settings
    character.voice_settings = {
        "voice_id": voice_settings.voice_id,
        "voice_enabled": voice_settings.voice_enabled,
        "voice_speed": voice_settings.voice_speed
    }

    await db.commit()
    await db.refresh(character)

    return {
        "success": True,
        "character_id": character_id,
        "voice_settings": character.voice_settings
    }


@router.get("/characters/{character_id}/voice")
async def get_character_voice(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get voice settings for a character"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Get voice settings or defaults
    voice_settings = character.voice_settings or {}

    if not voice_settings:
        # Set default based on persona
        default_voice = tts_service.get_voice_for_persona(character.persona_type)
        voice_settings = {
            "voice_id": default_voice,
            "voice_enabled": False,
            "voice_speed": 1.0
        }

    return {
        "character_id": character_id,
        "character_name": character.name,
        "voice_settings": voice_settings
    }


# Health Check

@router.get("/health")
async def voice_health_check():
    """Check health of voice services"""
    tts_check = tts_service.check_piper_installed()
    stt_loaded = stt_service.is_model_loaded()

    downloaded_voices = tts_service.list_downloaded_models()

    return {
        "tts": {
            "available": tts_check and len(downloaded_voices) > 0,
            "piper_installed": tts_check,
            "voices_downloaded": len(downloaded_voices)
        },
        "stt": {
            "available": stt_loaded,
            "model_loaded": stt_loaded,
            "model_info": stt_service.get_model_info() if stt_loaded else None
        }
    }
