from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.response import APIResponse
from app.schemas.doctor.update import DoctorProfileUpdate

from app.services.doctor.update import update_doctor_profile
from app.services.doctor.profile import get_doctor_profile
from app.utils.get_current_doctor import get_current_doctor_user



# ==========================================================
# DOCTOR PROFILE MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/profile",
    tags=["Doctor - Profile Management"],
)


# ==========================================================
# RETRIEVE DOCTOR PROFILE INFORMATION
# ==========================================================
@router.get(
    "",
    response_model=APIResponse,
)
def get_profile(
    db: Session = Depends(get_db),
    doctor_id: int = Depends(get_current_doctor_user),
):
    """
    Retrieve the authenticated doctor's profile details.
    """

    # ------------------------------------------------------
    # Fetch doctor profile information from the profile service
    # ------------------------------------------------------
    results = get_doctor_profile(
        db=db,
        doctor_id=doctor_id,
    )

    # ------------------------------------------------------
    # Return standardized response containing profile data
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )


# ==========================================================
# UPDATE DOCTOR PROFILE INFORMATION
# ==========================================================
@router.put(
    "",
    response_model=APIResponse,
)
def update_profile(
    profile_data: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    doctor_id: int = Depends(get_current_doctor_user),
):
    """
    Update the authenticated doctor's profile information.
    """

    # ------------------------------------------------------
    # Apply profile changes using the update service
    # ------------------------------------------------------
    results = update_doctor_profile(
        db=db,
        doctor_id=doctor_id,
        profile_data=profile_data,
    )

    # ------------------------------------------------------
    # Return standardized response with updated profile data
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )