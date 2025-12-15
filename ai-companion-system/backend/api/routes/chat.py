"""
Chat API Routes
Handles chat conversations with streaming support
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List, Optional
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from database.db import get_db
from api.models import Character, Message, User
from api.services.llm_service import llm_service
from api.services.memory_service import memory_service
from api.services.image_service import image_service
from config import settings


router = APIRouter()


class ChatRequest(BaseModel):
    character_id: int
    message: str
    user_id: int = 1
    stream: bool = True
    include_memory: bool = True


class ChatResponse(BaseModel):
    message_id: int
    content: str
    character_id: int
    generation_time: float
    tokens_used: int
    image_generated: Optional[str] = None


@router.post("/send")
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Send a message to a character"""
    result = await db.execute(
        select(Character).where(Character.id == request.character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    user_message = Message(
        character_id=request.character_id,
        user_id=request.user_id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()

    result = await db.execute(
        select(Message)
        .where(Message.character_id == request.character_id)
        .order_by(desc(Message.timestamp))
        .limit(settings.CONVERSATION_HISTORY_LIMIT)
    )
    history = result.scalars().all()

    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(history)
    ]

    memories = []
    if request.include_memory and settings.MEMORY_ENABLED:
        memories_data = await memory_service.retrieve_memories(
            request.character_id,
            request.message,
            limit=5
        )
        memories = [mem["content"] for mem in memories_data]

    character_info = {
        "id": character.id,
        "name": character.name,
        "persona_type": character.persona_type,
        "personality": character.personality,
        "backstory": character.backstory,
        "interests": character.interests,
        "speaking_style": character.speaking_style,
        "appearance_description": character.appearance_description
    }

    if request.stream:
        return StreamingResponse(
            stream_chat_response(
                messages,
                character_info,
                memories,
                db,
                request.character_id,
                request.user_id
            ),
            media_type="text/event-stream"
        )
    else:
        response = await llm_service.generate_response(
            messages,
            character_info,
            memories,
            stream=False
        )

        assistant_message = Message(
            character_id=request.character_id,
            user_id=request.user_id,
            role="assistant",
            content=response["content"],
            tokens_used=response.get("tokens", {}).get("total", 0),
            generation_time=response["generation_time"]
        )
        db.add(assistant_message)
        await db.commit()
        await db.refresh(assistant_message)

        if settings.MEMORY_ENABLED:
            await memory_service.add_memory(
                request.character_id,
                f"User said: {request.message}",
                memory_type="episodic",
                importance=0.7
            )
            await memory_service.add_memory(
                request.character_id,
                f"I responded: {response['content']}",
                memory_type="episodic",
                importance=0.6
            )

        return ChatResponse(
            message_id=assistant_message.id,
            content=response["content"],
            character_id=request.character_id,
            generation_time=response["generation_time"],
            tokens_used=response.get("tokens", {}).get("total", 0)
        )


async def stream_chat_response(
    messages: List[dict],
    character_info: dict,
    memories: List[str],
    db: AsyncSession,
    character_id: int,
    user_id: int
):
    """Stream chat response"""
    try:
        full_response = ""
        tokens_used = 0
        generation_time = 0

        response_gen = llm_service._generate_streaming(
            [{"role": "system", "content": llm_service._build_system_prompt(character_info)}] + messages,
            0
        )

        for chunk in response_gen:
            if chunk.get("type") == "chunk":
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk['content']})}\n\n"
                full_response += chunk["content"]
            elif chunk.get("type") == "done":
                generation_time = chunk.get("generation_time", 0)

        assistant_message = Message(
            character_id=character_id,
            user_id=user_id,
            role="assistant",
            content=full_response,
            tokens_used=tokens_used,
            generation_time=generation_time
        )
        db.add(assistant_message)
        await db.commit()
        await db.refresh(assistant_message)

        if settings.MEMORY_ENABLED:
            user_msg = messages[-1]["content"]
            await memory_service.add_memory(
                character_id,
                f"User said: {user_msg}",
                memory_type="episodic",
                importance=0.7
            )
            await memory_service.add_memory(
                character_id,
                f"I responded: {full_response}",
                memory_type="episodic",
                importance=0.6
            )

        should_generate_image = await llm_service.should_generate_image(
            full_response,
            messages
        )

        image_url = None
        if should_generate_image and settings.SD_ENABLED:
            try:
                image_prompt = await llm_service.generate_image_prompt(
                    full_response,
                    character_info.get("appearance_description", ""),
                    "expressing emotions or thoughts"
                )

                image_result = await image_service.generate_image(
                    prompt=image_prompt,
                    style="realistic",
                    character_id=character_id
                )

                image_url = image_result["file_url"]

            except Exception as e:
                print(f"Image generation failed: {e}")

        yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_message.id, 'generation_time': generation_time, 'image_url': image_url})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"


@router.get("/history/{character_id}")
async def get_chat_history(
    character_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a character"""
    result = await db.execute(
        select(Message)
        .where(Message.character_id == character_id)
        .order_by(desc(Message.timestamp))
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()

    return {
        "character_id": character_id,
        "messages": [msg.to_dict() for msg in reversed(messages)],
        "count": len(messages)
    }


@router.delete("/history/{character_id}")
async def clear_chat_history(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Clear chat history for a character"""
    result = await db.execute(
        select(Message).where(Message.character_id == character_id)
    )
    messages = result.scalars().all()

    for msg in messages:
        await db.delete(msg)

    await db.commit()

    return {"message": "Chat history cleared", "deleted_count": len(messages)}
