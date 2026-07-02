from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.response import APIResponse

from app.services.admin.dashboard import (
    get_admin_dashboard_data,
)


from app.schemas.contact.ContactCreate import ContactCreate
from app.services.contact_service.contact_service import process_contact_form

from app.utils.get_current_admin import get_real_admin_id


# ==========================================================
# ADMINISTRATOR DASHBOARD MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/dashboard",
    tags=["Administrator - Dashboard"],
)


# ==========================================================
# RETRIEVE ADMINISTRATOR DASHBOARD STATISTICS
# ==========================================================
@router.get(
    "",
    response_model=APIResponse,
)
def admin_dashboard(
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_real_admin_id),
):
    """
    Retrieve dashboard statistics and summary information
    for the authenticated administrator.
    """

    # ------------------------------------------------------
    # Fetch administrator dashboard data from the dashboard service
    # ------------------------------------------------------
    results = get_admin_dashboard_data(
        db=db,
        admin_id=admin_id,
    )

    # ------------------------------------------------------
    # Return standardized response containing dashboard data
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        details=results["detail"],
        data=results.get("data"),
    )



# ==========================================================
# RECEIVE CONTACT DETAILS
# ==========================================================
@router.post(
    "/contact",
    response_model=APIResponse,
)
def submit_contact_form(
    payload: ContactCreate,
    db: Session = Depends(get_db),
):

    results = process_contact_form(db, payload)

    return APIResponse(
        status_code=results["status_code"],
        details=results["details"],
        
    )