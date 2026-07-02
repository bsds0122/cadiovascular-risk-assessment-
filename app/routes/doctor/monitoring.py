from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.response import APIResponse
from app.services.patient.monitor import get_patient_monthly_monitoring
from app.utils.get_current_doctor import get_current_doctor_user



# ==========================================================
# DOCTOR PATIENT MONITORING MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/monitoring",
    tags=["Doctor - Patient Monitoring"],
)


# ==========================================================
# RETRIEVE YEARLY PATIENT MONITORING RECORDS
# ==========================================================
@router.get(
    "/patients/{patient_id}/yearly",
    response_model=APIResponse,
)
def get_patient_yearly_monitoring(
    patient_id: int,
    year: int,
    db: Session = Depends(get_db),
    doctor_id: int = Depends(get_current_doctor_user),
):
    """
    Retrieve a patient's yearly monitoring records,
    including assessment history and health progress.
    """

    # ------------------------------------------------------
    # Retrieve patient monitoring data for the specified year
    # ------------------------------------------------------
    results = get_patient_monthly_monitoring(
        db=db,
        patient_id=patient_id,
        year=year,
    )

    # ------------------------------------------------------
    # Return standardized API response with monitoring data
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )