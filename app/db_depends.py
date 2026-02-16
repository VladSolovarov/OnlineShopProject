from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield async sqlalchemy session for using db"""
    async with async_session_maker() as session:
        yield session