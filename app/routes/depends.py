from collections.abc import AsyncIterator
from http import HTTPStatus
from typing import Literal

import httpx
from fastapi import Depends, Header, HTTPException, Query
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JOSEError, jwk, jwt

from app.constants import Language
from app.db import get_async_session_maker
from app.db.uow import DBUnitOfWork
from app.schemas.options import FilterOptions, PaginationOptions, SortOptions
from app.schemas.places import LocationBounds
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


async def get_pagination_options(  # noqa: RUF029
    page: int | None = Query(1, ge=1),
    page_size: int | None = Query(10, ge=1),
) -> PaginationOptions | None:
    """Get the pagination options.

    Args:
        page (int, optional): The page number. Defaults to None.
        page_size (int, optional): The number of items per page. Defaults to None.

    Returns:
        PaginationOptions | None: The pagination options.

    """
    if not page_size:
        return None

    return PaginationOptions(page=page, page_size=page_size)


async def get_sort_options(  # noqa: RUF029
    sort_by: str | None = Query(None),
    order: Literal["asc", "desc"] | None = Query("asc"),
) -> SortOptions | None:
    """Get the sort options.

    Args:
        sort_by (str, optional): The field to sort by.
        order (Literal["asc", "desc"], optional): The order to sort by. Defaults to "asc".

    Returns:
        SortOptions | None: The sort options.

    """
    if not sort_by:
        return None

    return SortOptions(sort_by=sort_by, order=order)


async def get_filter_options(  # noqa: RUF029
    q: str | None = Query(None),
) -> FilterOptions | None:
    """Get the filter options.

    Args:
        q (str, optional): The query to filter by.

    Returns:
        FilterOptions | None: The filter options.

    """
    if not q:
        return None

    return FilterOptions(q=q)


async def get_location_bounds(  # noqa: RUF029
    sw_lat: float = Query(-90),
    sw_lng: float = Query(-180),
    ne_lat: float = Query(90),
    ne_lng: float = Query(180),
) -> LocationBounds:
    """Get the location bounds.

    Args:
        sw_lat (float): The south-west latitude.
        sw_lng (float): The south-west longitude.
        ne_lat (float): The north-east latitude.
        ne_lng (float): The north-east longitude.

    Returns:
        LocationBounds: The location bounds.

    """
    return LocationBounds(sw_lat=sw_lat, sw_lng=sw_lng, ne_lat=ne_lat, ne_lng=ne_lng)
