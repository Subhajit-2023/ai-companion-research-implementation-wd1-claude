"""
Database models for AI Companion System
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database.db import Base


class User(Base):
    """User model - for potential multi-user support"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON, default={})

    # Relationships
    characters = relationship("Character", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Character(Base):
    """AI Character/Companion model"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    persona_type = Column(String(50), default="custom")  # girlfriend, therapist, friend, custom
    personality = Column(Text)  # Personality description
    backstory = Column(Text)  # Character backstory
    interests = Column(JSON, default=[])  # List of interests
    speaking_style = Column(Text)  # How the character speaks
    system_prompt = Column(Text)  # Custom system prompt
    avatar_url = Column(String(500))  # Avatar image path/URL
    appearance_description = Column(Text)  # For image generation prompts
    voice_settings = Column(JSON, default={})  # For future voice feature
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})  # Additional settings

    # Relationships
    user = relationship("User", back_populates="characters")
    messages = relationship("Message", back_populates="character", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="character", cascade="all, delete-orphan")
    images = relationship("GeneratedImage", back_populates="character", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', persona='{self.persona_type}')>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "persona_type": self.persona_type,
            "personality": self.personality,
            "backstory": self.backstory,
            "interests": self.interests,
            "speaking_style": self.speaking_style,
            "avatar_url": self.avatar_url,
            "appearance_description": self.appearance_description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
        }


class Message(Base):
    """Chat message model"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    image_urls = Column(JSON, default=[])  # Associated images
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    tokens_used = Column(Integer, default=0)
    generation_time = Column(Float, default=0.0)  # Time in seconds
    metadata = Column(JSON, default={})  # Additional data (emotions, etc.)

    # Relationships
    user = relationship("User", back_populates="messages")
    character = relationship("Character", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', character_id={self.character_id})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "role": self.role,
            "content": self.content,
            "image_urls": self.image_urls,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tokens_used": self.tokens_used,
            "generation_time": self.generation_time,
            "metadata": self.metadata,
        }


class Memory(Base):
    """Long-term memory storage"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    memory_type = Column(String(50), default="episodic")  # episodic, semantic, emotional
    content = Column(Text, nullable=False)
    importance = Column(Float, default=1.0)  # 0.0 to 1.0
    embedding_id = Column(String(255))  # Reference to vector DB
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    accessed_at = Column(DateTime, default=datetime.utcnow)  # For decay
    access_count = Column(Integer, default=0)
    metadata = Column(JSON, default={})

    # Relationships
    character = relationship("Character", back_populates="memories")

    def __repr__(self):
        return f"<Memory(id={self.id}, type='{self.memory_type}', character_id={self.character_id})>"


class GeneratedImage(Base):
    """Generated image records"""
    __tablename__ = "generated_images"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500))
    width = Column(Integer, default=1024)
    height = Column(Integer, default=1024)
    steps = Column(Integer, default=30)
    cfg_scale = Column(Float, default=7.0)
    seed = Column(Integer)
    model_used = Column(String(200))
    generation_time = Column(Float)  # Time in seconds
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON, default={})  # LoRAs, etc.

    # Relationships
    character = relationship("Character", back_populates="images")

    def __repr__(self):
        return f"<GeneratedImage(id={self.id}, character_id={self.character_id})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "prompt": self.prompt,
            "file_url": self.file_url,
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata,
        }
