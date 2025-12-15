"""
Image Generation API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from database.db import get_db
from api.models import GeneratedImage, Character
from api.services.image_service import image_service
from config import settings


router = APIRouter()


class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    style: str = "realistic"
    width: Optional[int] = None
    height: Optional[int] = None
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    seed: int = -1
    character_id: Optional[int] = None
    user_id: int = 1


class CharacterImageRequest(BaseModel):
    character_id: int
    situation: str = "portrait"
    style: str = "realistic"
    user_id: int = 1


@router.post("/generate")
async def generate_image(
    request: ImageGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate an image from a prompt"""
    if not settings.SD_ENABLED:
        raise HTTPException(status_code=503, detail="Image generation is disabled")

    available = await image_service.check_availability()
    if not available:
        raise HTTPException(
            status_code=503,
            detail="Stable Diffusion API is not available"
        )

    try:
        result = await image_service.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            style=request.style,
            width=request.width,
            height=request.height,
            steps=request.steps,
            cfg_scale=request.cfg_scale,
            seed=request.seed,
            character_id=request.character_id,
            enhance_prompt=True
        )

        image_record = GeneratedImage(
            user_id=request.user_id,
            character_id=request.character_id,
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
            metadata={"style": result["style"]}
        )

        db.add(image_record)
        await db.commit()
        await db.refresh(image_record)

        return {
            "success": True,
            "image": image_record.to_dict(),
            "generation_time": result["generation_time"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-character")
async def generate_character_image(
    request: CharacterImageRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate an image for a character"""
    if not settings.SD_ENABLED:
        raise HTTPException(status_code=503, detail="Image generation is disabled")

    result = await db.execute(
        select(Character).where(Character.id == request.character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if not character.appearance_description:
        raise HTTPException(
            status_code=400,
            detail="Character has no appearance description"
        )

    try:
        character_info = {
            "id": character.id,
            "name": character.name,
            "appearance_description": character.appearance_description
        }

        result = await image_service.generate_character_image(
            character_info,
            situation=request.situation,
            style=request.style
        )

        image_record = GeneratedImage(
            user_id=request.user_id,
            character_id=request.character_id,
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
            metadata={"style": result["style"], "situation": request.situation}
        )

        db.add(image_record)
        await db.commit()
        await db.refresh(image_record)

        return {
            "success": True,
            "image": image_record.to_dict(),
            "generation_time": result["generation_time"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gallery")
async def get_image_gallery(
    character_id: Optional[int] = None,
    user_id: int = 1,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get image gallery"""
    query = select(GeneratedImage).where(GeneratedImage.user_id == user_id)

    if character_id:
        query = query.where(GeneratedImage.character_id == character_id)

    query = query.order_by(desc(GeneratedImage.created_at)).limit(limit).offset(offset)

    result = await db.execute(query)
    images = result.scalars().all()

    return {
        "images": [img.to_dict() for img in images],
        "count": len(images)
    }


@router.get("/{image_id}")
async def get_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific image"""
    result = await db.execute(
        select(GeneratedImage).where(GeneratedImage.id == image_id)
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    return image.to_dict()


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an image"""
    result = await db.execute(
        select(GeneratedImage).where(GeneratedImage.id == image_id)
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = Path(image.file_path)
    if file_path.exists():
        file_path.unlink()

    await db.delete(image)
    await db.commit()

    return {"message": "Image deleted successfully"}


@router.get("/status/check")
async def check_sd_status():
    """Check Stable Diffusion API status"""
    if not settings.SD_ENABLED:
        return {
            "enabled": False,
            "available": False,
            "message": "Image generation is disabled in settings"
        }

    available = await image_service.check_availability()
    models = await image_service.get_available_models() if available else []

    return {
        "enabled": True,
        "available": available,
        "models": models,
        "current_model": settings.SD_MODEL
    }
