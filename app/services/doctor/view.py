from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.models.doctors import Doctor


# ==========================================================
# DOCTOR SERIALIZATION HELPERS
# ==========================================================

def doctor_to_dict(doctor):
    """
    Convert a doctor ORM object into a detailed dictionary.
    Used for profile and single doctor views.
    """

    return {
        "doctor_id": doctor.doctor_id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "phone": doctor.phone,
        "specialization": doctor.specialization,
        "experience_years": doctor.experience_years,
        "hospital": doctor.hospital,
        "license_number": doctor.license_number,
        "profile_image": doctor.profile_image,
        "email": doctor.user.email if doctor.user else None,
        "is_active": doctor.user.is_active if doctor.user else None,
    }


def doctor_summary_to_dict(doctor):
    """
    Convert a doctor ORM object into a lightweight dictionary.
    Used for list views and search results.
    """

    return {
        "doctor_id": doctor.doctor_id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "email": doctor.user.email if doctor.user else None,
        "profile_image": doctor.profile_image,
    }


# ==========================================================
# GET ALL DOCTORS (PAGINATED)
# ==========================================================
def get_all_doctors(
    db: Session,
    skip: int = 0,
    limit: int = 15,
):
    """
    Retrieve a paginated list of doctors.
    Supports offset-based pagination.
    """

    try:
        # --------------------------------------------------
        # Validate pagination parameters
        # --------------------------------------------------
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid page number.",
            )

        if limit < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid page size.",
            )

        # --------------------------------------------------
        # Fetch doctors with user relationship
        # --------------------------------------------------
        doctors = (
            db.query(Doctor)
            .options(joinedload(Doctor.user))
            .offset(skip)
            .limit(limit)
            .all()
        )

        # --------------------------------------------------
        # Format response
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Doctors retrieved successfully.",
            "data": [
                doctor_summary_to_dict(doctor)
                for doctor in doctors
            ],
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve doctors.",
        )


# ==========================================================
# GET SINGLE DOCTOR BY ID
# ==========================================================
def get_doctor_by_id(
    db: Session,
    doctor_id: int,
):
    """
    Retrieve a single doctor profile using doctor ID.
    Includes linked user account details.
    """

    try:
        # Fetch doctor with user relationship
        doctor = (
            db.query(Doctor)
            .options(joinedload(Doctor.user))
            .filter(Doctor.doctor_id == doctor_id)
            .first()
        )

        # Validate existence
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found.",
            )

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Doctor profile retrieved successfully.",
            "data": doctor_to_dict(doctor),
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve doctor information.",
        )


# ==========================================================
# SEARCH DOCTORS BY NAME
# ==========================================================
def search_doctors(
    db: Session,
    name: str,
):
    """
    Search doctors by first name or last name.
    Supports partial matching and ranking of results.
    """

    try:
        # --------------------------------------------------
        # Validate input
        # --------------------------------------------------
        if not name or not name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter a doctor name.",
            )

        search_term = name.strip().lower()

        # --------------------------------------------------
        # Query doctors with case-insensitive search
        # --------------------------------------------------
        doctors = (
            db.query(Doctor)
            .options(joinedload(Doctor.user))
            .filter(
                (Doctor.first_name.ilike(f"%{search_term}%")) |
                (Doctor.last_name.ilike(f"%{search_term}%"))
            )
            .all()
        )

        # --------------------------------------------------
        # Rank results: exact match > prefix match > others
        # --------------------------------------------------
        doctors.sort(
            key=lambda doctor: (
                not (
                    doctor.first_name.lower() == search_term
                    or doctor.last_name.lower() == search_term
                ),
                not (
                    doctor.first_name.lower().startswith(search_term)
                    or doctor.last_name.lower().startswith(search_term)
                ),
                doctor.first_name.lower(),
            )
        )

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Doctors retrieved successfully.",
            "data": [
                doctor_summary_to_dict(doctor)
                for doctor in doctors
            ],
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to search doctors.",
        )