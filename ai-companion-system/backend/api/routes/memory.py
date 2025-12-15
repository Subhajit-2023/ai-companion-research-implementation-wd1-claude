"""
Memory Management API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from api.services.memory_service import memory_service
from config import settings


router = APIRouter()


class MemoryAddRequest(BaseModel):
    character_id: int
    content: str
    memory_type: str = "episodic"
    importance: float = 1.0


class MemorySearchRequest(BaseModel):
    character_id: int
    query: str
    limit: Optional[int] = None
    memory_type: Optional[str] = None
    min_importance: float = 0.0


@router.post("/add")
async def add_memory(request: MemoryAddRequest):
    """Add a memory for a character"""
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    memory_id = await memory_service.add_memory(
        request.character_id,
        request.content,
        memory_type=request.memory_type,
        importance=request.importance
    )

    return {
        "success": True,
        "memory_id": memory_id,
        "character_id": request.character_id
    }


@router.post("/search")
async def search_memories(request: MemorySearchRequest):
    """Search character memories"""
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    memories = await memory_service.retrieve_memories(
        request.character_id,
        request.query,
        limit=request.limit,
        memory_type=request.memory_type,
        min_importance=request.min_importance
    )

    return {
        "character_id": request.character_id,
        "query": request.query,
        "memories": memories,
        "count": len(memories)
    }


@router.get("/recent/{character_id}")
async def get_recent_memories(
    character_id: int,
    limit: int = 10
):
    """Get recent memories for a character"""
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    memories = await memory_service.get_recent_memories(
        character_id,
        limit=limit
    )

    return {
        "character_id": character_id,
        "memories": memories,
        "count": len(memories)
    }


@router.get("/stats/{character_id}")
async def get_memory_stats(character_id: int):
    """Get memory statistics for a character"""
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    stats = await memory_service.get_memory_stats(character_id)

    return {
        "character_id": character_id,
        "stats": stats
    }


@router.delete("/{character_id}")
async def clear_memories(character_id: int):
    """Clear all memories for a character"""
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    await memory_service.clear_character_memories(character_id)

    return {
        "message": "Memories cleared successfully",
        "character_id": character_id
    }
