from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Request

from app.routes.places import router as places_router
from app.routes.tags import router as tags_router
from app.routes.tag_types import router as tag_types_router
from app.services.errors import CustomError


app = FastAPI(docs_url="/")
app.include_router(places_router)
app.include_router(tags_router)
app.include_router(tag_types_router)


@app.exception_handler(CustomError)
async def handle_custom_error(request: Request, exc: Exception):
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail=str(exc),
    )
