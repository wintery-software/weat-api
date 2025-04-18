from typing import AsyncIterator

from fastapi import Header, Query

from app.constants import Language
from app.db import async_session_maker
from app.models.uow import DBUnitOfWork


async def get_db() -> AsyncIterator[DBUnitOfWork]:
    async with DBUnitOfWork(async_session_maker) as uow:
        yield uow


async def get_lang(
    lang: str | None = Query(None),
    accept_language: str | None = Header(None, alias="Accept-Language"),
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
