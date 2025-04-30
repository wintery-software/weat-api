import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_async_engine_and_session
from app.routes.places import router as places_router
from app.routes.tag_types import router as tag_types_router
from app.routes.tags import router as tags_router
from app.services.errors import CustomError


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:  # noqa: RUF029
    """Lifespan context manager for FastAPI application.

    Args:
        _app (FastAPI): The FastAPI application instance.

    Yields:
        None: Yields control to the application context.

    """
    init_async_engine_and_session()

    yield


app = FastAPI(docs_url="/", lifespan=lifespan)
app.include_router(places_router)
app.include_router(tags_router)
app.include_router(tag_types_router)


@app.exception_handler(CustomError)
def handle_custom_error(_request: Request, exc: CustomError) -> None:
    """Handle custom errors.

    Args:
        _request (Request): The request object.
        exc (Exception): The exception to handle.

    Raises:
        HTTPException: Raises an HTTP exception with a 400 status code and the error message.

    """
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail=exc.message,
    )


origins = os.getenv("CORS_ALLOW_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
