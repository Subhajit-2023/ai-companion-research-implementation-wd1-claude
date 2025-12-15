"""
Character Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from database.db import get_db
from api.models import Character, User
from config import settings, CHARACTER_TEMPLATES


router = APIRouter()


class CharacterCreate(BaseModel):
    name: str
    persona_type: str = "custom"
    personality: Optional[str] = None
    backstory: Optional[str] = None
    interests: List[str] = []
    speaking_style: Optional[str] = None
    appearance_description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_id: int = 1


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    backstory: Optional[str] = None
    interests: Optional[List[str]] = None
    speaking_style: Optional[str] = None
    appearance_description: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/")
async def list_characters(
    user_id: int = 1,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all characters for a user"""
    query = select(Character).where(Character.user_id == user_id)

    if active_only:
        query = query.where(Character.is_active == True)

    result = await db.execute(query)
    characters = result.scalars().all()

    return {
        "characters": [char.to_dict() for char in characters],
        "count": len(characters)
    }


@router.get("/{character_id}")
async def get_character(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific character"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return character.to_dict()


@router.post("/")
async def create_character(
    character_data: CharacterCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new character"""
    result = await db.execute(
        select(User).where(User.id == character_data.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(id=character_data.user_id, username=f"user_{character_data.user_id}")
        db.add(user)
        await db.commit()

    result = await db.execute(
        select(Character).where(Character.user_id == character_data.user_id)
    )
    existing_chars = result.scalars().all()

    if len(existing_chars) >= settings.MAX_CHARACTERS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum number of characters ({settings.MAX_CHARACTERS_PER_USER}) reached"
        )

    character = Character(
        user_id=character_data.user_id,
        name=character_data.name,
        persona_type=character_data.persona_type,
        personality=character_data.personality,
        backstory=character_data.backstory,
        interests=character_data.interests,
        speaking_style=character_data.speaking_style,
        appearance_description=character_data.appearance_description,
        system_prompt=character_data.system_prompt
    )

    db.add(character)
    await db.commit()
    await db.refresh(character)

    return character.to_dict()


@router.put("/{character_id}")
async def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing character"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    update_data = character_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)

    await db.commit()
    await db.refresh(character)

    return character.to_dict()


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a character"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    from api.services.memory_service import memory_service
    await memory_service.clear_character_memories(character_id)

    await db.delete(character)
    await db.commit()

    return {"message": "Character deleted successfully"}


@router.post("/from-template")
async def create_from_template(
    template_name: str,
    user_id: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Create a character from a template"""
    if template_name not in CHARACTER_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")

    template = CHARACTER_TEMPLATES[template_name]

    character_data = CharacterCreate(
        user_id=user_id,
        name=template["name"],
        persona_type=template_name,
        personality=template["personality"],
        backstory=template["backstory"],
        interests=template["interests"],
        speaking_style=template["speaking_style"]
    )

    return await create_character(character_data, db)


@router.get("/templates/list")
async def list_templates():
    """List available character templates"""
    return {
        "templates": [
            {
                "name": name,
                "display_name": template["name"],
                "personality": template["personality"],
                "description": template["backstory"][:100] + "..."
            }
            for name, template in CHARACTER_TEMPLATES.items()
        ]
    }


@router.post("/{character_id}/avatar")
async def generate_character_avatar(
    character_id: int,
    style: str = "realistic",
    db: AsyncSession = Depends(get_db)
):
    """Generate an avatar for the character"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if not character.appearance_description:
        raise HTTPException(
            status_code=400,
            detail="Character has no appearance description"
        )

    from api.services.image_service import image_service

    try:
        image_result = await image_service.generate_character_image(
            {
                "id": character.id,
                "name": character.name,
                "appearance_description": character.appearance_description
            },
            situation="portrait",
            style=style
        )

        character.avatar_url = image_result["file_url"]
        await db.commit()

        return {
            "message": "Avatar generated successfully",
            "avatar_url": image_result["file_url"],
            "generation_time": image_result["generation_time"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {str(e)}")
