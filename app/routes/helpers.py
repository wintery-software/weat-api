from collections.abc import AsyncIterator
from http import HTTPStatus

import httpx
from fastapi import Depends, Header, HTTPException, Query
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JOSEError, jwk, jwt

from app.constants import Language
from app.db import get_async_session_maker
from app.models.uow import DBUnitOfWork
from app.settings import settings

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.aws_cognito_authorization_url,
    tokenUrl=settings.aws_cognito_token_url,
)


async def get_db() -> AsyncIterator[DBUnitOfWork]:
    """Dependency that provides a database session for the request.

    Yields:
        DBUnitOfWork: The database unit of work.

    """
    async_session_maker = get_async_session_maker()
    async with DBUnitOfWork(async_session_maker) as uow:
        yield uow


async def get_lang(  # noqa: RUF029
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


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict | None:
    """Get the current user from the token.

    Args:
        token (str): The JWT token.

    Raises:
        HTTPException: If the token is invalid or expired.

    Returns:
        dict | None: The decoded token payload.

    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(settings.aws_cognito_jwks_url)
        jwks = resp.json()["keys"]

    unverified_header = jwt.get_unverified_header(token)
    key = next((k for k in jwks if k["kid"] == unverified_header["kid"]), None)

    if key is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token header")

    public_key = jwk.construct(
        {
            "kty": key["kty"],
            "n": key["n"],
            "e": key["e"],
        },
        algorithm="RS256",
    )

    try:
        return jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=settings.aws_cognito_client_id,
            issuer=settings.aws_cognito_issuer,
        )
    except JOSEError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token header") from e


async def get_admin_user(  # noqa: RUF029
    user: dict = Depends(get_current_user),
) -> dict:
    """Get the admin user from the token.

    Args:
        token (str): The JWT token.
        user (dict): The decoded token payload.

    Raises:
        HTTPException: If the user is not an admin.

    Returns:
        dict: The decoded token payload.

    """
    if not user.get("cognito:groups") or "admin" not in user["cognito:groups"]:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Not an admin user")

    return user
