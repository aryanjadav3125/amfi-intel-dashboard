from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import get_db_session

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a transactional async database session.
    """
    async with get_db_session() as session:
        yield session
