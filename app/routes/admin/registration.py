from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.admin.register import AdminRegister
from app.schemas.response import APIResponse

from app.services.admin.register import register_admin


# ==========================================================
# ADMINISTRATOR ACCOUNT MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="",
    tags=["Administrator Management"],
)


# ==========================================================
# REGISTER A NEW ADMINISTRATOR ACCOUNT
# ==========================================================
@router.post(
    "/register",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_admin(
    admin_data: AdminRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new administrator account and create
    the administrator profile.
    """

    # ------------------------------------------------------
    # Create a new administrator account in the system
    # ------------------------------------------------------
    result = register_admin(
        db=db,
        admin_data=admin_data,
    )

    # ------------------------------------------------------
    # Return standardized response with administrator details
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )