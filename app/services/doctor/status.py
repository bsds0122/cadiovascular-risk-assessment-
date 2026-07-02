from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.doctors import Doctor
from app.models.user import User


# ==========================================================
# TOGGLE DOCTOR ACCOUNT STATUS (ACTIVATE / DEACTIVATE)
# ==========================================================
def toggle_doctor_status(
    db: Session,
    doctor_id: int,
    is_active: bool,
):
    """
    Activate or deactivate a doctor's account.
    This affects the linked User account.
    """

    try:
        # --------------------------------------------------
        # STEP 1: Check if doctor exists
        # --------------------------------------------------
        doctor = (
            db.query(Doctor)
            .filter(Doctor.doctor_id == doctor_id)
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

        # --------------------------------------------------
        # STEP 2: Fetch linked user account
        # --------------------------------------------------
        user = (
            db.query(User)
            .filter(User.user_id == doctor.user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor account not found.",
            )

        # --------------------------------------------------
        # STEP 3: Prevent unnecessary updates
        # --------------------------------------------------
        if user.is_active == is_active:
            message = (
                "Account already active."
                if is_active
                else "Account already inactive."
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

        # --------------------------------------------------
        # STEP 4: Update account status
        # --------------------------------------------------
        user.is_active = is_active

        # Save changes
        db.commit()
        db.refresh(user)

        # --------------------------------------------------
        # STEP 5: Return response
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_200_OK,
            "detail": (
                "Account activated successfully."
                if is_active
                else "Account deactivated successfully."
            ),
            "data": {
                "doctor_id": doctor.doctor_id,
                "is_active": user.is_active,
            },
        }

    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update account status.",
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )