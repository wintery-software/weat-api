from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Request

from sqlalchemy.exc import IntegrityError, NoResultFound

from app.routes.places import router as places_router


app = FastAPI(docs_url="/")
app.include_router(places_router)


@app.exception_handler(IntegrityError)
async def handle_integrity_error(request: Request, exc: IntegrityError):
    detail = str(exc.orig).split("\n")[0]
    raise HTTPException(
        status_code=HTTPStatus.BAD_REQUEST,
        detail=f"Object already exists: {detail}",
    )


@app.exception_handler(NoResultFound)
async def handle_no_result_round_error(request: Request, exc: NoResultFound):
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail=f"Object not found",
    )
