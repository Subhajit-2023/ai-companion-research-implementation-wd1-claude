"""
Character Routes - Handle character management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from database.db import get_db
from api.models import Character, User
from api.services.memory_service import memory_service
from config import settings, CHARACTER_TEMPLATES, SYSTEM_PROMPTS

router = APIRouter()


class CharacterCreate(BaseModel):
    name: str
    persona_type: str = "custom"
    personality: Optional[str] = None
    backstory: Optional[str] = None
    interests: List[str] = []
    speaking_style: Optional[str] = None
    appearance_description: Optional[str] = None
    user_id: int = 1


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    backstory: Optional[str] = None
    interests: Optional[List[str]] = None
    speaking_style: Optional[str] = None
    appearance_description: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/")
async def list_characters(
    user_id: int = 1,
    db: AsyncSession = Depends(get_db),
):
    """List all characters for a user"""
    result = await select(Character).where(Character.user_id == user_id)
    characters = (await db.execute(result)).scalars().all()

    return {
        "characters": [char.to_dict() for char in characters],
        "total": len(characters),
    }


@router.get("/{character_id}")
async def get_character(
    character_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific character"""
    result = await select(Character).where(Character.id == character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    memory_stats = await memory_service.get_memory_stats(character_id)

    return {
        **character.to_dict(),
        "memory_stats": memory_stats,
    }


@router.post("/")
async def create_character(
    character_data: CharacterCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new character"""
    result = await select(Character).where(Character.user_id == character_data.user_id)
    existing_characters = (await db.execute(result)).scalars().all()

    if len(existing_characters) >= settings.MAX_CHARACTERS_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.MAX_CHARACTERS_PER_USER} characters per user"
        )

    template = CHARACTER_TEMPLATES.get(character_data.persona_type)

    if template and not character_data.personality:
        character_data.personality = template["personality"]
        character_data.backstory = template["backstory"]
        character_data.interests = template["interests"]
        character_data.speaking_style = template["speaking_style"]

    system_prompt = SYSTEM_PROMPTS.get(character_data.persona_type, SYSTEM_PROMPTS["default"])

    character = Character(
        user_id=character_data.user_id,
        name=character_data.name,
        persona_type=character_data.persona_type,
        personality=character_data.personality,
        backstory=character_data.backstory,
        interests=character_data.interests,
        speaking_style=character_data.speaking_style,
        system_prompt=system_prompt,
        appearance_description=character_data.appearance_description,
    )

    db.add(character)
    await db.commit()
    await db.refresh(character)

    return character.to_dict()


@router.put("/{character_id}")
async def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a character"""
    result = await select(Character).where(Character.id == character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    update_data = character_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(character, key, value)

    character.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(character)

    return character.to_dict()


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a character"""
    result = await select(Character).where(Character.id == character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    await memory_service.clear_character_memories(character_id)

    await db.delete(character)
    await db.commit()

    return {"message": "Character deleted successfully"}


@router.get("/presets/list")
async def list_character_presets():
    """List available character presets"""
    presets = []

    for preset_name, template in CHARACTER_TEMPLATES.items():
        presets.append({
            "type": preset_name,
            "name": template["name"],
            "personality": template["personality"],
            "interests": template["interests"],
            "backstory": template["backstory"],
        })

    return {"presets": presets}


@router.post("/{character_id}/memories")
async def add_character_memory(
    character_id: int,
    content: str,
    memory_type: str = "episodic",
    importance: float = 0.5,
    db: AsyncSession = Depends(get_db),
):
    """Manually add a memory for a character"""
    result = await select(Character).where(Character.id == character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    memory_id = await memory_service.add_memory(
        character_id=character_id,
        content=content,
        memory_type=memory_type,
        importance=importance,
    )

    return {
        "message": "Memory added successfully",
        "memory_id": memory_id,
    }


@router.get("/{character_id}/memories")
async def get_character_memories(
    character_id: int,
    query: Optional[str] = None,
    n_results: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get character memories"""
    result = await select(Character).where(Character.id == character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if query:
        memories = await memory_service.retrieve_memories(
            character_id=character_id,
            query=query,
            n_results=n_results,
        )
    else:
        memories = await memory_service.get_recent_memories(
            character_id=character_id,
            n_results=n_results,
        )

    return {
        "character_id": character_id,
        "memories": memories,
        "total": len(memories),
    }


@router.delete("/{character_id}/memories")
async def clear_character_memories(
    character_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Clear all memories for a character"""
    result = await select(Character).where(Character.id == character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    success = await memory_service.clear_character_memories(character_id)

    if success:
        return {"message": "Memories cleared successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear memories")
