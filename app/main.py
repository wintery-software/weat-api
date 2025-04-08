from fastapi import FastAPI

from app.routes.places import router as places_router


app = FastAPI()
app.include_router(places_router)
