"""
Initialize database and create default user
Run this script once before starting the application
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from database.db import init_db, async_session_maker
from api.models import User
from sqlalchemy import select


async def create_default_user():
    """Create default user if not exists"""
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                id=1,
                username="default_user",
                settings={}
            )
            session.add(user)
            await session.commit()
            print("✓ Created default user")
        else:
            print("✓ Default user already exists")


async def main():
    """Main initialization"""
    print("="*50)
    print("AI Companion System - Database Initialization")
    print("="*50)
    print()

    print("Initializing database...")
    await init_db()

    print("Creating default user...")
    await create_default_user()

    print()
    print("="*50)
    print("Database initialization complete!")
    print("="*50)
    print()
    print("You can now start the application:")
    print("  python -m api.main")


if __name__ == "__main__":
    asyncio.run(main())
