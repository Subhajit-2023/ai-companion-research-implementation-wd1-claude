"""
Chat Routes - Handle conversation endpoints
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
from api.models import Character, Message, User, GeneratedImage
from api.services.llm_service import llm_service
from api.services.memory_service import memory_service
from api.services.search_service import search_service
from api.services.image_service import image_service
from config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    character_id: int
    message: str
    user_id: int = 1
    stream: bool = True


class ChatResponse(BaseModel):
    message_id: int
    content: str
    character_id: int
    generation_time: float
    tokens_used: int
    image_url: Optional[str] = None


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to a character and get response (non-streaming)
    """
    result = await select(Character).where(Character.id == request.character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    result = await select(Message).where(
        Message.character_id == request.character_id,
        Message.user_id == request.user_id,
    ).order_by(desc(Message.timestamp)).limit(settings.CONVERSATION_HISTORY_LIMIT)

    recent_messages = (await db.execute(result)).scalars().all()
    recent_messages = list(reversed(recent_messages))

    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in recent_messages
    ]

    conversation_history.append({"role": "user", "content": request.message})

    user_message = Message(
        character_id=request.character_id,
        user_id=request.user_id,
        role="user",
        content=request.message,
    )
    db.add(user_message)
    await db.commit()

    relevant_memories = []
    if settings.MEMORY_ENABLED:
        memories = await memory_service.retrieve_memories(
            character_id=request.character_id,
            query=request.message,
            n_results=5,
        )
        relevant_memories = [mem["content"] for mem in memories]

    search_results_text = None
    if settings.ENABLE_WEB_SEARCH:
        should_search = await search_service.should_search(request.message, llm_service)
        if should_search:
            search_query = await search_service.extract_search_query(request.message, llm_service)
            search_results = await search_service.search(search_query, max_results=3)
            if search_results:
                search_results_text = await search_service.format_search_results_for_llm(
                    search_results, search_query
                )
                relevant_memories.append(f"Web search results: {search_results_text}")

    character_info = character.to_dict()

    response = await llm_service.generate_response(
        messages=conversation_history,
        character_info=character_info,
        memories=relevant_memories if relevant_memories else None,
        stream=False,
    )

    assistant_message = Message(
        character_id=request.character_id,
        user_id=request.user_id,
        role="assistant",
        content=response["content"],
        tokens_used=response.get("tokens", {}).get("total", 0),
        generation_time=response["generation_time"],
    )
    db.add(assistant_message)
    await db.commit()

    if settings.MEMORY_ENABLED:
        await memory_service.extract_and_store_memory(
            character_id=request.character_id,
            user_message=request.message,
            assistant_response=response["content"],
            llm_service=llm_service,
            importance=0.6,
        )

    image_url = None
    if settings.SD_ENABLED:
        should_generate = await llm_service.should_generate_image(
            response["content"], conversation_history
        )

        if should_generate and character.appearance_description:
            image_result = await image_service.generate_character_image(
                character_info=character_info,
                situation="expressing thoughts during conversation",
                style="realistic",
            )

            if image_result.get("success"):
                image_url = image_result["file_url"]

                generated_image = GeneratedImage(
                    character_id=request.character_id,
                    user_id=request.user_id,
                    prompt=image_result["prompt"],
                    negative_prompt=image_result["negative_prompt"],
                    file_path=image_result["file_path"],
                    file_url=image_result["file_url"],
                    width=image_result["width"],
                    height=image_result["height"],
                    steps=image_result["steps"],
                    cfg_scale=image_result["cfg_scale"],
                    seed=image_result["seed"],
                    model_used=image_result["model"],
                    generation_time=image_result["generation_time"],
                    metadata={"style": image_result["style"]},
                )
                db.add(generated_image)

                assistant_message.image_urls = [image_url]

                await db.commit()

    return ChatResponse(
        message_id=assistant_message.id,
        content=response["content"],
        character_id=request.character_id,
        generation_time=response["generation_time"],
        tokens_used=response.get("tokens", {}).get("total", 0),
        image_url=image_url,
    )


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message and stream the response
    """
    result = await select(Character).where(Character.id == request.character_id)
    character = (await db.execute(result)).scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    result = await select(Message).where(
        Message.character_id == request.character_id,
        Message.user_id == request.user_id,
    ).order_by(desc(Message.timestamp)).limit(settings.CONVERSATION_HISTORY_LIMIT)

    recent_messages = (await db.execute(result)).scalars().all()
    recent_messages = list(reversed(recent_messages))

    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in recent_messages
    ]

    conversation_history.append({"role": "user", "content": request.message})

    user_message = Message(
        character_id=request.character_id,
        user_id=request.user_id,
        role="user",
        content=request.message,
    )
    db.add(user_message)
    await db.commit()

    relevant_memories = []
    if settings.MEMORY_ENABLED:
        memories = await memory_service.retrieve_memories(
            character_id=request.character_id,
            query=request.message,
            n_results=5,
        )
        relevant_memories = [mem["content"] for mem in memories]

    character_info = character.to_dict()

    async def event_generator():
        stream = llm_service.generate_response(
            messages=conversation_history,
            character_info=character_info,
            memories=relevant_memories if relevant_memories else None,
            stream=True,
        )

        full_response = ""
        async for chunk in stream:
            if chunk.get("type") == "chunk":
                full_response += chunk["content"]
                yield f"data: {json.dumps(chunk)}\n\n"
            elif chunk.get("type") == "done":
                assistant_message = Message(
                    character_id=request.character_id,
                    user_id=request.user_id,
                    role="assistant",
                    content=full_response,
                    tokens_used=0,
                    generation_time=chunk["generation_time"],
                )
                db.add(assistant_message)
                await db.commit()

                if settings.MEMORY_ENABLED:
                    await memory_service.extract_and_store_memory(
                        character_id=request.character_id,
                        user_message=request.message,
                        assistant_response=full_response,
                        llm_service=llm_service,
                        importance=0.6,
                    )

                yield f"data: {json.dumps(chunk)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.get("/history/{character_id}")
async def get_chat_history(
    character_id: int,
    user_id: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get chat history for a character"""
    result = await select(Message).where(
        Message.character_id == character_id,
        Message.user_id == user_id,
    ).order_by(desc(Message.timestamp)).limit(limit)

    messages = (await db.execute(result)).scalars().all()
    messages = list(reversed(messages))

    return {
        "character_id": character_id,
        "messages": [msg.to_dict() for msg in messages],
        "total": len(messages),
    }


@router.delete("/history/{character_id}")
async def clear_chat_history(
    character_id: int,
    user_id: int = 1,
    db: AsyncSession = Depends(get_db),
):
    """Clear chat history for a character"""
    result = await select(Message).where(
        Message.character_id == character_id,
        Message.user_id == user_id,
    )

    messages = (await db.execute(result)).scalars().all()

    for message in messages:
        await db.delete(message)

    await db.commit()

    return {"message": "Chat history cleared", "deleted_count": len(messages)}
