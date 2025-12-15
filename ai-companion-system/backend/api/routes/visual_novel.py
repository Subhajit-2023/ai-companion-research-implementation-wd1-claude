"""
Visual Novel API Routes
Handles story progression, scene navigation, and choice management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from database.db import get_db
from api.models_vn import VisualNovel, VNScene, VNPlaySession, VNGeneratedAsset
from api.services.image_service import image_service
from api.services.llm_service import llm_service

router = APIRouter()


class StartSessionRequest(BaseModel):
    visual_novel_id: int
    user_id: int = 1
    save_name: Optional[str] = None


class MakeChoiceRequest(BaseModel):
    session_id: int
    choice_index: int


class SaveSessionRequest(BaseModel):
    session_id: int
    save_name: str


@router.get("/novels")
async def list_visual_novels(
    db: AsyncSession = Depends(get_db),
):
    """List all available visual novels"""
    result = await select(VisualNovel).where(VisualNovel.is_active == True)
    novels = (await db.execute(result)).scalars().all()

    return {
        "novels": [novel.to_dict() for novel in novels],
        "total": len(novels),
    }


@router.get("/novels/{novel_id}")
async def get_visual_novel(
    novel_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific visual novel"""
    result = await select(VisualNovel).where(VisualNovel.id == novel_id)
    novel = (await db.execute(result)).scalar_one_or_none()

    if not novel:
        raise HTTPException(status_code=404, detail="Visual novel not found")

    scenes_result = await select(VNScene).where(VNScene.visual_novel_id == novel_id)
    scenes = (await db.execute(scenes_result)).scalars().all()

    return {
        **novel.to_dict(),
        "scene_count": len(scenes),
    }


@router.post("/sessions/start")
async def start_play_session(
    request: StartSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Start a new playthrough session"""
    novel_result = await select(VisualNovel).where(VisualNovel.id == request.visual_novel_id)
    novel = (await db.execute(novel_result)).scalar_one_or_none()

    if not novel:
        raise HTTPException(status_code=404, detail="Visual novel not found")

    first_scene_result = await select(VNScene).where(
        and_(
            VNScene.visual_novel_id == request.visual_novel_id,
            VNScene.scene_number == 1
        )
    )
    first_scene = (await db.execute(first_scene_result)).scalar_one_or_none()

    if not first_scene:
        raise HTTPException(status_code=500, detail="Visual novel has no starting scene")

    session = VNPlaySession(
        user_id=request.user_id,
        visual_novel_id=request.visual_novel_id,
        current_scene_id=first_scene.id,
        save_name=request.save_name or f"Save {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "session": session.to_dict(),
        "current_scene": first_scene.to_dict(),
    }


@router.get("/sessions/{session_id}")
async def get_play_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get current play session state"""
    result = await select(VNPlaySession).where(VNPlaySession.id == session_id)
    session = (await db.execute(result)).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Play session not found")

    if session.current_scene_id:
        scene_result = await select(VNScene).where(VNScene.id == session.current_scene_id)
        current_scene = (await db.execute(scene_result)).scalar_one_or_none()
    else:
        current_scene = None

    return {
        "session": session.to_dict(),
        "current_scene": current_scene.to_dict() if current_scene else None,
    }


@router.get("/sessions/user/{user_id}")
async def list_user_sessions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """List all play sessions for a user"""
    result = await select(VNPlaySession).where(VNPlaySession.user_id == user_id)
    sessions = (await db.execute(result)).scalars().all()

    session_list = []
    for session in sessions:
        novel_result = await select(VisualNovel).where(VisualNovel.id == session.visual_novel_id)
        novel = (await db.execute(novel_result)).scalar_one_or_none()

        session_list.append({
            **session.to_dict(),
            "novel_title": novel.title if novel else "Unknown",
        })

    return {
        "sessions": session_list,
        "total": len(session_list),
    }


@router.post("/sessions/{session_id}/advance")
async def advance_scene(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Advance to the next scene (for linear progression)"""
    session_result = await select(VNPlaySession).where(VNPlaySession.id == session_id)
    session = (await db.execute(session_result)).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Play session not found")

    current_scene_result = await select(VNScene).where(VNScene.id == session.current_scene_id)
    current_scene = (await db.execute(current_scene_result)).scalar_one_or_none()

    if not current_scene:
        raise HTTPException(status_code=500, detail="Current scene not found")

    if current_scene.is_ending:
        session.is_completed = True
        session.ending_reached = current_scene.metadata.get("ending_name", "Ending")
        await db.commit()

        return {
            "message": "Story completed!",
            "ending": session.ending_reached,
            "session": session.to_dict(),
        }

    if current_scene.scene_type == "choice":
        return {
            "message": "This is a choice scene. Use /make-choice endpoint",
            "current_scene": current_scene.to_dict(),
        }

    if not current_scene.next_scene_id:
        raise HTTPException(status_code=500, detail="No next scene defined")

    next_scene_result = await select(VNScene).where(VNScene.id == current_scene.next_scene_id)
    next_scene = (await db.execute(next_scene_result)).scalar_one_or_none()

    if not next_scene:
        raise HTTPException(status_code=500, detail="Next scene not found")

    session.current_scene_id = next_scene.id
    session.scenes_completed.append(current_scene.id)
    session.last_played = datetime.utcnow()

    await db.commit()
    await db.refresh(session)

    return {
        "session": session.to_dict(),
        "current_scene": next_scene.to_dict(),
    }


@router.post("/sessions/{session_id}/choice")
async def make_choice(
    session_id: int,
    request: MakeChoiceRequest,
    db: AsyncSession = Depends(get_db),
):
    """Make a choice in a choice scene"""
    session_result = await select(VNPlaySession).where(VNPlaySession.id == session_id)
    session = (await db.execute(session_result)).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Play session not found")

    current_scene_result = await select(VNScene).where(VNScene.id == session.current_scene_id)
    current_scene = (await db.execute(current_scene_result)).scalar_one_or_none()

    if not current_scene or current_scene.scene_type != "choice":
        raise HTTPException(status_code=400, detail="Current scene is not a choice scene")

    if not current_scene.choices or request.choice_index >= len(current_scene.choices):
        raise HTTPException(status_code=400, detail="Invalid choice index")

    choice = current_scene.choices[request.choice_index]
    next_scene_id = choice.get("next_scene_id")

    if not next_scene_id:
        raise HTTPException(status_code=500, detail="Choice has no next scene defined")

    next_scene_result = await select(VNScene).where(VNScene.id == next_scene_id)
    next_scene = (await db.execute(next_scene_result)).scalar_one_or_none()

    if not next_scene:
        raise HTTPException(status_code=500, detail="Next scene not found")

    session.current_scene_id = next_scene.id
    session.scenes_completed.append(current_scene.id)
    session.choices_made.append({
        "scene_id": current_scene.id,
        "choice_index": request.choice_index,
        "choice_text": choice.get("text"),
        "timestamp": datetime.utcnow().isoformat(),
    })
    session.last_played = datetime.utcnow()

    if choice.get("flags"):
        for flag, value in choice["flags"].items():
            session.flags[flag] = value

    await db.commit()
    await db.refresh(session)

    return {
        "choice_made": choice,
        "session": session.to_dict(),
        "current_scene": next_scene.to_dict(),
    }


@router.post("/scenes/{scene_id}/generate-image")
async def generate_scene_image(
    scene_id: int,
    asset_type: str = "background",
    db: AsyncSession = Depends(get_db),
):
    """Generate image for a scene"""
    scene_result = await select(VNScene).where(VNScene.id == scene_id)
    scene = (await db.execute(scene_result)).scalar_one_or_none()

    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    if asset_type == "background":
        prompt = scene.background_image_prompt
    elif asset_type == "character":
        prompt = scene.character_image_prompt
    else:
        raise HTTPException(status_code=400, detail="Invalid asset type")

    if not prompt:
        raise HTTPException(status_code=400, detail="No prompt defined for this asset type")

    result = await image_service.generate_image(
        prompt=prompt,
        style="anime",
        width=1024,
        height=768 if asset_type == "background" else 1024,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=f"Image generation failed: {result.get('error')}")

    asset = VNGeneratedAsset(
        scene_id=scene_id,
        asset_type=asset_type,
        prompt=prompt,
        file_path=result["file_path"],
        file_url=result["file_url"],
        generation_params={
            "style": "anime",
            "steps": result["steps"],
            "seed": result["seed"],
        },
    )

    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    return asset.to_dict()


@router.get("/scenes/{scene_id}/assets")
async def get_scene_assets(
    scene_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all generated assets for a scene"""
    result = await select(VNGeneratedAsset).where(VNGeneratedAsset.scene_id == scene_id)
    assets = (await db.execute(result)).scalars().all()

    return {
        "assets": [asset.to_dict() for asset in assets],
        "total": len(assets),
    }


@router.delete("/sessions/{session_id}")
async def delete_play_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a play session (save file)"""
    result = await select(VNPlaySession).where(VNPlaySession.id == session_id)
    session = (await db.execute(result)).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Play session not found")

    await db.delete(session)
    await db.commit()

    return {"message": "Play session deleted successfully"}
