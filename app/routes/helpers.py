from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Language
from app.db import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_lang(
    lang: Optional[str] = Query(None),
    accept_language: Optional[str] = Header(None, alias="Accept-Language"),
) -> Language:
    resolved = "en-US"

    if lang:
        resolved = lang
    elif accept_language:
        resolved = accept_language.split(",")[0].strip()

    try:
        return Language(resolved)
    except ValueError:
        return Language.EN_US
