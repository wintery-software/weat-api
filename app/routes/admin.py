from fastapi import APIRouter, Depends

from app.routes.depends import get_admin_user
from app.routes.places import protected_router as places_router
from app.routes.tag_types import protected_router as tag_types_router
from app.routes.tags import protected_router as tags_router

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_admin_user)])

router.include_router(places_router)
router.include_router(tags_router)
router.include_router(tag_types_router)
