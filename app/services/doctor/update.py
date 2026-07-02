from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.doctors import Doctor


# ==========================================================
# UPDATE DOCTOR PROFILE
# ==========================================================
def update_doctor_profile(
    db: Session,
    doctor_id: int,
    profile_data,
):
    """
    Update doctor profile information using provided fields only.
    Partial updates are supported.
    """

    try:
        # --------------------------------------------------
        # STEP 1: Retrieve doctor by ID
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
        # STEP 2: Extract only provided fields (PATCH behavior)
        # --------------------------------------------------
        update_data = profile_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No information provided for update.",
            )

        # --------------------------------------------------
        # STEP 3: Apply updates dynamically
        # --------------------------------------------------
        for field, value in update_data.items():
            setattr(doctor, field, value)

        # --------------------------------------------------
        # STEP 4: Save changes to database
        # --------------------------------------------------
        db.commit()
        db.refresh(doctor)

        # --------------------------------------------------
        # STEP 5: Return updated doctor profile
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Profile updated successfully.",
            "data": {
                "doctor_id": doctor.doctor_id,
                "user_id": doctor.user_id,
                "first_name": doctor.first_name,
                "last_name": doctor.last_name,
                "phone": doctor.phone,
                "specialization": doctor.specialization,
                "experience_years": doctor.experience_years,
                "hospital": doctor.hospital,
                "license_number": doctor.license_number,
                "profile_image": doctor.profile_image,
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
            detail="Unable to update doctor profile.",
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )