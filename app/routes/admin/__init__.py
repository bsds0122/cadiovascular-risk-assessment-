from fastapi import APIRouter

from app.routes.admin.registration import router as registration_router
from app.routes.admin.doctors import router as doctors_router
from app.routes.admin.dashboard import router as dashboard_router
from app.routes.admin.profile import router as profile_router


router = APIRouter(
    prefix="/admin"
)

router.include_router(registration_router)
router.include_router(doctors_router)
router.include_router(dashboard_router)
router.include_router(profile_router)
