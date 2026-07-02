from fastapi import APIRouter

from app.routes.doctor.dashboard import router as dashboard_router
from app.routes.doctor.patients import router as patients_router
from app.routes.doctor.assessments import router as assessments_router
from app.routes.doctor.monitoring import router as monitoring_router
from app.routes.doctor.profile import router as profile_router

router = APIRouter(
    prefix="/doctor"
)

router.include_router(dashboard_router)
router.include_router(patients_router)
router.include_router(assessments_router)
router.include_router(monitoring_router)
router.include_router(profile_router)
