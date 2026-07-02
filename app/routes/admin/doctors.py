from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.response import APIResponse
from app.schemas.doctor.register import DoctorRegister
from app.schemas.doctor.update import DoctorProfileUpdate

from app.services.doctor.register import register_doctor
from app.services.doctor.register_excel import register_doctors_excel
from app.services.doctor.view import (
    get_all_doctors,
    get_doctor_by_id,
    search_doctors,
)
from app.services.doctor.status import toggle_doctor_status
from app.services.doctor.update import update_doctor_profile


from app.utils.get_current_admin import get_real_admin_id


# ==========================================================
# ADMINISTRATOR DOCTOR MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/doctors",
    tags=["Administrator - Doctor Management"],
)


# ==========================================================
# REGISTER A NEW DOCTOR ACCOUNT
# ==========================================================
@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctor(
    doctor_data: DoctorRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new doctor account and create the doctor's profile.
    This endpoint allows new doctor registration.
    """

    # ------------------------------------------------------
    # Create a new doctor account in the system
    # ------------------------------------------------------
    result = register_doctor(
        db=db,
        doctor_data=doctor_data,
    )

    # ------------------------------------------------------
    # Return standardized response with doctor information
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )


# ==========================================================
# REGISTER MULTIPLE DOCTORS USING AN EXCEL FILE
# ==========================================================
@router.post(
    "/bulk",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_doctors_bulk(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Register multiple doctors by uploading an Excel file.
    """

    # ------------------------------------------------------
    # Process the uploaded Excel file and create doctor records
    # ------------------------------------------------------
    result = register_doctors_excel(
        db=db,
        file=file,
    )

    # ------------------------------------------------------
    # Return bulk registration processing results
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )


# ==========================================================
# RETRIEVE ALL REGISTERED DOCTORS WITH PAGINATION
# ==========================================================
@router.get(
    "",
    response_model=APIResponse,
)
def view_doctors(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Retrieve a paginated list of all registered doctors.
    """

    # ------------------------------------------------------
    # Fetch doctor records based on pagination parameters
    # ------------------------------------------------------
    result = get_all_doctors(
        db=db,
        skip=skip,
        limit=limit,
    )

    # ------------------------------------------------------
    # Return doctor list and pagination data
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )


# ==========================================================
# SEARCH DOCTORS BY NAME
# ==========================================================
@router.get(
    "/search",
    response_model=APIResponse,
)
def search_for_doctors(
    name: str,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Search for doctors using their name.
    """

    # ------------------------------------------------------
    # Find doctors matching the provided search term
    # ------------------------------------------------------
    result = search_doctors(
        db=db,
        name=name,
    )

    # ------------------------------------------------------
    # Return matching doctor records
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )


# ==========================================================
# RETRIEVE A SINGLE DOCTOR PROFILE
# ==========================================================
@router.get(
    "/{doctor_id}",
    response_model=APIResponse,
)
def get_doctor_profile(
    doctor_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Retrieve detailed information for a specific doctor.
    """

    # ------------------------------------------------------
    # Fetch doctor profile using the doctor identifier
    # ------------------------------------------------------
    result = get_doctor_by_id(
        db=db,
        doctor_id=doctor_id,
    )

    # ------------------------------------------------------
    # Return doctor profile information
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )


# ==========================================================
# UPDATE DOCTOR PROFILE INFORMATION
# ==========================================================
@router.put(
    "/{doctor_id}",
    response_model=APIResponse,
)
def edit_doctor(
    doctor_id: int,
    doctor_data: DoctorProfileUpdate,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Update an existing doctor's profile information.
    """

    # ------------------------------------------------------
    # Apply changes to the doctor's profile
    # ------------------------------------------------------
    result = update_doctor_profile(
        db=db,
        doctor_id=doctor_id,
        profile_data=doctor_data,
    )

    # ------------------------------------------------------
    # Return updated doctor profile details
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )


# ==========================================================
# ACTIVATE A DOCTOR ACCOUNT
# ==========================================================
@router.put(
    "/{doctor_id}/activate",
    response_model=APIResponse,
)
def activate_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Activate a doctor's account and allow system access.
    """

    # ------------------------------------------------------
    # Enable the doctor's account status
    # ------------------------------------------------------
    result = toggle_doctor_status(
        db=db,
        doctor_id=doctor_id,
        is_active=True,
    )

    # ------------------------------------------------------
    # Return activation confirmation
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )


# ==========================================================
# DEACTIVATE A DOCTOR ACCOUNT
# ==========================================================
@router.put(
    "/{doctor_id}/deactivate",
    response_model=APIResponse,
)
def deactivate_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Deactivate a doctor's account and restrict system access.
    """

    # ------------------------------------------------------
    # Disable the doctor's account status
    # ------------------------------------------------------
    result = toggle_doctor_status(
        db=db,
        doctor_id=doctor_id,
        is_active=False,
    )

    # ------------------------------------------------------
    # Return deactivation confirmation
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
        data=result.get("data"),
    )

