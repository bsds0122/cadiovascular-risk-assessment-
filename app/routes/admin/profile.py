from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.response import APIResponse
from app.schemas.admin.update import AdministratorProfileUpdate

from app.services.admin.profile import (
    update_admin_profile,
    get_admin_profile,
)

from app.utils.get_current_admin import get_real_admin_id


# ==========================================================
# ADMINISTRATOR PROFILE MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/profile",
    tags=["Administrator - Profile Management"],
)


# ==========================================================
# RETRIEVE ADMINISTRATOR PROFILE INFORMATION
# ==========================================================
@router.get(
    "",
    response_model=APIResponse,
)
def view_profile(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Retrieve the authenticated administrator's profile information.
    """

    # ------------------------------------------------------
    # Fetch administrator profile details from the profile service
    # ------------------------------------------------------
    result = get_admin_profile(
        db=db,
        admin_id=admin_id,
    )

    # ------------------------------------------------------
    # Return standardized response containing administrator data
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )


# ==========================================================
# UPDATE ADMINISTRATOR PROFILE INFORMATION
# ==========================================================
@router.put(
    "",
    response_model=APIResponse,
)
def update_profile(
    profile_data: AdministratorProfileUpdate,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Update the authenticated administrator's profile information.
    """

    # ------------------------------------------------------
    # Apply changes to the administrator profile
    # ------------------------------------------------------
    result = update_admin_profile(
        db=db,
        admin_id=admin_id,
        profile_data=profile_data,
    )

    # ------------------------------------------------------
    # Return standardized response with updated profile details
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )