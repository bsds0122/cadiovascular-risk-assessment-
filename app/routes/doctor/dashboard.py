from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.get_current_doctor import get_current_doctor_user

from app.services.doctor.dashboard import get_dashboard_data

from app.schemas.response import APIResponse


# ==========================================================
# DOCTOR DASHBOARD MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ==========================================================
# RETRIEVE DOCTOR DASHBOARD STATISTICS
# ==========================================================
@router.get(
    "/",
    response_model=APIResponse,
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_doctor=Depends(get_current_doctor_user),
):
    """
    Retrieve dashboard statistics and summary information
    for the authenticated doctor.
    """

    # ------------------------------------------------------
    # Fetch dashboard data using the dashboard service
    # ------------------------------------------------------
    results = get_dashboard_data(
        db=db,
        current_doctor=current_doctor,
    )

    # ------------------------------------------------------
    # Return standardized API response with dashboard data
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )