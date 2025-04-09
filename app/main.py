from fastapi import FastAPI

from app.routes.places import router as places_router


app = FastAPI(docs_url="/")
app.include_router(places_router)
