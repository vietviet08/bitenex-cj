# API v1 routers
from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.events import router as events_router
from app.api.v1.identify import router as identify_router

router = APIRouter(prefix="/v1")

router.include_router(events_router, tags=["Events"])
router.include_router(identify_router, tags=["Identity"])
router.include_router(analytics_router, tags=["Analytics"])
