from fastapi import APIRouter

from app.routes.auth.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.doctor import router as doctor_router

router = APIRouter()

# Authentication
router.include_router(auth_router)

# Administrator
router.include_router(admin_router)

# Doctor
router.include_router(doctor_router)
