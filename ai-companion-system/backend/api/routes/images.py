"""
Image Generation Routes - Handle image generation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from database.db import get_db
from api.models import Character, GeneratedImage
from api.services.image_service import image_service
from api.services.llm_service import llm_service
from config import settings

router = APIRouter()


class ImageGenerationRequest(BaseModel):
    prompt: str
    character_id: Optional[int] = None
    user_id: int = 1
    style: str = "realistic"
    negative_prompt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    seed: int = -1
    enhance_prompt: bool = False


class CharacterImageRequest(BaseModel):
    character_id: int
    situation: str = "portrait"
    style: str = "realistic"
    user_id: int = 1


@router.get("/status")
async def get_image_generation_status():
    """Check if image generation is available"""
    api_available = await image_service.check_api_status()
    models = await image_service.get_available_models()

    return {
        "available": api_available,
        "enabled": settings.SD_ENABLED,
        "current_model": settings.SD_MODEL,
        "available_models": models,
    }


@router.get("/styles")
async def get_available_styles():
    """Get available art styles"""
    return {
        "styles": list(image_service.style_presets.keys()),
        "presets": image_service.style_presets,
    }


@router.post("/generate")
async def generate_image(
    request: ImageGenerationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate an image from a text prompt"""
    if not settings.SD_ENABLED:
        raise HTTPException(status_code=503, detail="Image generation is disabled")

    api_available = await image_service.check_api_status()
    if not api_available:
        raise HTTPException(
            status_code=503,
            detail="Stable Diffusion API is not available. Make sure SD WebUI is running with --api flag"
        )

    prompt = request.prompt

    if request.enhance_prompt:
        prompt = await image_service.enhance_prompt_with_llm(prompt, llm_service)

    result = await image_service.generate_image(
        prompt=prompt,
        negative_prompt=request.negative_prompt,
        style=request.style,
        width=request.width,
        height=request.height,
        steps=request.steps,
        cfg_scale=request.cfg_scale,
        seed=request.seed,
        character_id=request.character_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {result.get('error', 'Unknown error')}"
        )

    generated_image = GeneratedImage(
        character_id=request.character_id,
        user_id=request.user_id,
        prompt=result["prompt"],
        negative_prompt=result["negative_prompt"],
        file_path=result["file_path"],
        file_url=result["file_url"],
        width=result["width"],
        height=result["height"],
        steps=result["steps"],
        cfg_scale=result["cfg_scale"],
        seed=result["seed"],
        model_used=result["model"],
        generation_time=result["generation_time"],
        metadata={"style": result["style"]},
    )

    db.add(generated_image)
    await db.commit()
    await db.refresh(generated_image)

    return {
        **generated_image.to_dict(),
        "generation_time": result["generation_time"],
    }


@router.post("/generate-character")
async def generate_character_image(
    request: CharacterImageRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate an image of a character in a specific situation"""
    if not settings.SD_ENABLED:
        raise HTTPException(status_code=503, detail="Image generation is disabled")

    result = await select(Character).where(Character.id == request.character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if not character.appearance_description:
        raise HTTPException(
            status_code=400,
            detail="Character has no appearance description. Please add one in character settings."
        )

    character_info = character.to_dict()

    result = await image_service.generate_character_image(
        character_info=character_info,
        situation=request.situation,
        style=request.style,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {result.get('error', 'Unknown error')}"
        )

    generated_image = GeneratedImage(
        character_id=request.character_id,
        user_id=request.user_id,
        prompt=result["prompt"],
        negative_prompt=result["negative_prompt"],
        file_path=result["file_path"],
        file_url=result["file_url"],
        width=result["width"],
        height=result["height"],
        steps=result["steps"],
        cfg_scale=result["cfg_scale"],
        seed=result["seed"],
        model_used=result["model"],
        generation_time=result["generation_time"],
        metadata={
            "style": result["style"],
            "situation": request.situation,
        },
    )

    db.add(generated_image)
    await db.commit()
    await db.refresh(generated_image)

    return {
        **generated_image.to_dict(),
        "generation_time": result["generation_time"],
    }


@router.get("/history")
async def get_image_history(
    user_id: int = 1,
    character_id: Optional[int] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get image generation history"""
    query = select(GeneratedImage).where(GeneratedImage.user_id == user_id)

    if character_id:
        query = query.where(GeneratedImage.character_id == character_id)

    query = query.order_by(desc(GeneratedImage.created_at)).limit(limit)

    result = await db.execute(query)
    images = result.scalars().all()

    return {
        "images": [img.to_dict() for img in images],
        "total": len(images),
    }


@router.get("/{image_id}")
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific generated image"""
    result = await select(GeneratedImage).where(GeneratedImage.id == image_id)
    image = (await db.execute(result)).scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return image.to_dict()


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a generated image"""
    result = await select(GeneratedImage).where(GeneratedImage.id == image_id)
    image = (await db.execute(result)).scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = Path(image.file_path)
    if file_path.exists():
        file_path.unlink()

    await db.delete(image)
    await db.commit()

    return {"message": "Image deleted successfully"}


@router.post("/enhance-prompt")
async def enhance_prompt(
    prompt: str,
):
    """Enhance a basic prompt using LLM"""
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    enhanced = await image_service.enhance_prompt_with_llm(prompt, llm_service)

    return {
        "original_prompt": prompt,
        "enhanced_prompt": enhanced,
    }
