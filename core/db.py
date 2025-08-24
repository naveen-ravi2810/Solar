from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.settings import get_settings

engine: AsyncEngine = create_async_engine(get_settings.DB_URL)


async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:  # type: ignore
    async with async_session() as session:
        yield session
