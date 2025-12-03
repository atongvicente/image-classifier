from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings


settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False, future=True)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    session: AsyncSession = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
