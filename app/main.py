from http import HTTPStatus
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

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


origins = os.getenv("CORS_ALLOW_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
