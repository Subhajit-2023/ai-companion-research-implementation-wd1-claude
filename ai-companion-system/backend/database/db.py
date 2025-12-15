"""
Database setup and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config import settings, ensure_directories


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session

    Usage:
        @app.get("/")
        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    ensure_directories()

    # Import all models to ensure they're registered
    from api.models import Character, Message, Memory, User, GeneratedImage
    from api.models_vn import VisualNovel, VNScene, VNPlaySession, VNGeneratedAsset

    async with engine.begin() as conn:
        # Drop all tables (only for development)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("✓ Database initialized successfully (including Visual Novel tables)")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    print("✓ Database connections closed")


if __name__ == "__main__":
    import asyncio

    async def test_db():
        """Test database connection"""
        await init_db()

        async with async_session_maker() as session:
            result = await session.execute("SELECT 1")
            print(f"Database test query result: {result.scalar()}")

        await close_db()

    asyncio.run(test_db())
