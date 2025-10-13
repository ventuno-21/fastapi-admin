from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/mydb"
)
# sqlite for development:
# DATABASE_URL = "sqlite+aiosqlite:///./dev.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """
    Create database tables for all SQLModel/SQLAlchemy models that were imported.
    Call this at startup or before first use.
    """
    async with engine.begin() as conn:
        # If a new model being added, below line will create its table
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency for getting DB session."""
    async with AsyncSessionLocal() as session:
        yield session
