"""
Visual Novel System Database Models
Enables story-driven character experiences with branching narratives
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database.db import Base


class VisualNovel(Base):
    """Visual Novel Story definition"""
    __tablename__ = "visual_novels"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    author = Column(String(100))
    genre = Column(String(100))  # romance, mystery, horror, fantasy, etc.
    cover_image_url = Column(String(500))
    total_scenes = Column(Integer, default=0)
    estimated_playtime = Column(Integer)  # in minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})  # tags, warnings, etc.

    # Relationships
    scenes = relationship("VNScene", back_populates="visual_novel", cascade="all, delete-orphan")
    play_sessions = relationship("VNPlaySession", back_populates="visual_novel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<VisualNovel(id={self.id}, title='{self.title}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "genre": self.genre,
            "cover_image_url": self.cover_image_url,
            "total_scenes": self.total_scenes,
            "estimated_playtime": self.estimated_playtime,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata,
        }


class VNScene(Base):
    """Individual scene in a visual novel"""
    __tablename__ = "vn_scenes"

    id = Column(Integer, primary_key=True, index=True)
    visual_novel_id = Column(Integer, ForeignKey("visual_novels.id"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    chapter = Column(String(100))  # Chapter name/number
    title = Column(String(200))

    # Scene content
    narrative_text = Column(Text)  # The story text
    character_dialogue = Column(Text)  # Character speaking
    character_name = Column(String(100))  # Who is speaking

    # Visual elements
    background_image_prompt = Column(Text)  # For generating background
    character_image_prompt = Column(Text)  # For generating character sprite
    background_music = Column(String(200))  # Music track name

    # Scene type
    scene_type = Column(String(50), default="narrative")  # narrative, choice, ending

    # Choices (if scene_type = "choice")
    choices = Column(JSON, default=[])  # List of choice objects

    # Next scene navigation
    next_scene_id = Column(Integer, ForeignKey("vn_scenes.id"), nullable=True)
    is_ending = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

    # Relationships
    visual_novel = relationship("VisualNovel", back_populates="scenes")

    def __repr__(self):
        return f"<VNScene(id={self.id}, vn={self.visual_novel_id}, scene={self.scene_number})>"

    def to_dict(self):
        return {
            "id": self.id,
            "visual_novel_id": self.visual_novel_id,
            "scene_number": self.scene_number,
            "chapter": self.chapter,
            "title": self.title,
            "narrative_text": self.narrative_text,
            "character_dialogue": self.character_dialogue,
            "character_name": self.character_name,
            "background_image_prompt": self.background_image_prompt,
            "character_image_prompt": self.character_image_prompt,
            "background_music": self.background_music,
            "scene_type": self.scene_type,
            "choices": self.choices,
            "next_scene_id": self.next_scene_id,
            "is_ending": self.is_ending,
            "metadata": self.metadata,
        }


class VNPlaySession(Base):
    """User's playthrough of a visual novel"""
    __tablename__ = "vn_play_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    visual_novel_id = Column(Integer, ForeignKey("visual_novels.id"), nullable=False)

    # Progress tracking
    current_scene_id = Column(Integer, ForeignKey("vn_scenes.id"))
    scenes_completed = Column(JSON, default=[])  # List of completed scene IDs
    choices_made = Column(JSON, default=[])  # History of choices

    # Session data
    started_at = Column(DateTime, default=datetime.utcnow)
    last_played = Column(DateTime, default=datetime.utcnow)
    playtime_minutes = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    ending_reached = Column(String(100))  # Which ending was reached

    # Save data
    save_name = Column(String(100))  # Custom save name
    flags = Column(JSON, default={})  # Story flags/variables

    metadata = Column(JSON, default={})

    # Relationships
    visual_novel = relationship("VisualNovel", back_populates="play_sessions")

    def __repr__(self):
        return f"<VNPlaySession(id={self.id}, vn={self.visual_novel_id}, user={self.user_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "visual_novel_id": self.visual_novel_id,
            "current_scene_id": self.current_scene_id,
            "scenes_completed": self.scenes_completed,
            "choices_made": self.choices_made,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_played": self.last_played.isoformat() if self.last_played else None,
            "playtime_minutes": self.playtime_minutes,
            "is_completed": self.is_completed,
            "ending_reached": self.ending_reached,
            "save_name": self.save_name,
            "flags": self.flags,
            "metadata": self.metadata,
        }


class VNGeneratedAsset(Base):
    """Generated images/assets for visual novel scenes"""
    __tablename__ = "vn_generated_assets"

    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey("vn_scenes.id"), nullable=False)
    asset_type = Column(String(50))  # background, character_sprite, cg, etc.
    prompt = Column(Text)
    file_path = Column(String(500))
    file_url = Column(String(500))
    generation_params = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<VNGeneratedAsset(id={self.id}, scene={self.scene_id}, type={self.asset_type})>"

    def to_dict(self):
        return {
            "id": self.id,
            "scene_id": self.scene_id,
            "asset_type": self.asset_type,
            "prompt": self.prompt,
            "file_url": self.file_url,
            "generation_params": self.generation_params,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
