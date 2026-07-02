from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.assessment.create import AssessmentCreate
from app.schemas.response import APIResponse

from app.services.assessment.create import assess_patient
from app.services.assessment.view import  get_assessments_by_date



from app.utils.get_current_doctor import get_current_doctor_user



# ==========================================================
# DOCTOR ASSESSMENT MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/assessments",
    tags=["Doctor - Assessment Management"],
)




# ==========================================================
# CREATE SINGLE PATIENT ASSESSMENT
# ==========================================================
@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment(
    assessment_data: AssessmentCreate,
    db: Session = Depends(get_db),
    doctor_id: int = Depends(get_current_doctor_user),
):
    """
    Create a cardiovascular risk assessment for a patient.
    """

    results = await assess_patient(
        db=db,
        assessment_data=assessment_data,
    )

    return APIResponse(
        status_code=results["status_code"],
        details=results["details"],
        data=results.get("data"),
    )


# ==========================================================
# RETRIEVE PATIENT ASSESSMENT BY DATE
# ==========================================================
@router.get(
    "/patients/{patient_id}",
    response_model=APIResponse,
)
def get_patient_assessment(
    patient_id: int,
    year: int,
    month: int,
    day: int,
    db: Session = Depends(get_db),
    doctor_id: int = Depends(get_current_doctor_user),
):

    results = get_assessments_by_date(
        db=db,
        patient_id=patient_id,
        year=year,
        month=month,
        day=day,
    )

    return APIResponse(
        status_code=results["status_code"],
        details=results["details"],
        data=results["data"],
    )