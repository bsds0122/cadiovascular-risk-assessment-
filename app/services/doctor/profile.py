from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import traceback

from app.models.doctors import Doctor
from app.models.user import User


def get_doctor_profile(
    db: Session,
    doctor_id: int,
):
    try:
        doctor = (
            db.query(Doctor)
            .filter(Doctor.doctor_id == doctor_id)
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found.",
            )

        user = (
            db.query(User)
            .filter(User.user_id == doctor.user_id)
            .first()
        )

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Doctor profile retrieved successfully.",
            "data": {
                "doctor_id": doctor.doctor_id,
                "user_id": doctor.user_id,

                "first_name": doctor.first_name,
                "last_name": doctor.last_name,

                "email": user.email if user else None,

                "phone": doctor.phone,
                "specialization": doctor.specialization,
                "experience_years": doctor.experience_years,
                "hospital": doctor.hospital,
                "license_number": doctor.license_number,
                "profile_image": doctor.profile_image,
            },
        }

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        print(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Database error while retrieving doctor profile.",
                "error": str(e),
            },
        )

    except Exception as e:
        print(traceback.format_exc())

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Unexpected error occurred.",
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )