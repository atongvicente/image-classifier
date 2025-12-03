from collections.abc import AsyncGenerator

from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession

from .database import get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


def get_image_service(request: Request):
    return request.app.state.image_service


def get_settings(request: Request):
    return request.app.state.settings
