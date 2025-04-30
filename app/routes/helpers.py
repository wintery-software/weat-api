from collections.abc import AsyncIterator

from fastapi import Header, Query

from app.constants import Language
from app.db import async_session_maker
from app.models.uow import DBUnitOfWork


async def get_db() -> AsyncIterator[DBUnitOfWork]:
    """Dependency that provides a database session for the request.

    Yields:
        DBUnitOfWork: The database unit of work.

    """
    async with DBUnitOfWork(async_session_maker) as uow:
        yield uow


def get_lang(
    lang: str | None = Query(None),
    accept_language: str | None = Header(None, alias="Accept-Language"),
) -> Language:
    """Get the language from the query parameter or the Accept-Language header.

    Args:
        lang (str, optional): The language code from the query parameter. Defaults to None.
        accept_language (str, optional): The Accept-Language header value. Defaults to None.

    Returns:
        Language: The resolved language.

    """
    resolved = "en-US"

    if lang:
        resolved = lang
    elif accept_language:
        resolved = accept_language.split(",")[0].strip()

    try:
        return Language(resolved)
    except ValueError:
        return Language.EN_US
