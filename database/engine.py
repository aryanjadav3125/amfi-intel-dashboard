from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger("database.engine")

# Construct async connection URL
DATABASE_URL = settings.DATABASE_URL

# For SQLite, we must ensure we enable thread safety and check same thread configuration
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

logger.info(f"Initializing database engine on: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

# Create Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True
)

# Async Session Factory
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Declarative Base
Base = declarative_base()

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Exposes an async context manager for robust transaction management.
    """
    session = AsyncSessionFactory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session rolled back due to error: {e}")
        raise e
    finally:
        await session.close()
        
async def init_models():
    """
    Initializes tables synchronously inside test or dev environments.
    """
    async with engine.begin() as conn:
        logger.info("Verifying and executing schema creation...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Schema verification finished.")
