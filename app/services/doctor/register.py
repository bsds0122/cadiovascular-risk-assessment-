import secrets
import string

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.models.doctors import Doctor
from app.utils.security import hash_password


# ==========================================================
# TEMPORARY PASSWORD GENERATION (SECURE CREDENTIAL CREATION)
# ==========================================================
def generate_password(length: int = 10) -> str:
    """
    Generate a secure random temporary password
    for newly registered doctor accounts.
    """

    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


# ==========================================================
# SINGLE DOCTOR REGISTRATION SERVICE
# ==========================================================
def register_doctor(
    db: Session,
    doctor_data,
):
    """
    Register a new doctor account and create an associated profile.

    Process:
    - Validate email uniqueness
    - Validate medical license uniqueness
    - Create authentication user account
    - Create doctor profile record
    - Return credentials for initial login
    """

    try:
        # --------------------------------------------------
        # Validate email uniqueness (authentication layer)
        # --------------------------------------------------
        # existing_user = (
            # db.query(User)
            # .filter(User.email == doctor_data.email)
            # .first()
        # )

        # if existing_user:
            # raise HTTPException(
                # status_code=status.HTTP_409_CONFLICT,
                # detail="Email already registered.",
            # )

        # --------------------------------------------------
        # Validate medical license uniqueness (clinical identity)
        # --------------------------------------------------
        # existing_license = (
            # db.query(Doctor)
            # .filter(
                # Doctor.license_number == doctor_data.license_number
            # )
            # .first()
        # )

        # if existing_license:
            # raise HTTPException(
                # status_code=status.HTTP_409_CONFLICT,
                # detail="License number already exists.",
            # )

        # --------------------------------------------------
        # Generate secure temporary password
        # --------------------------------------------------
        temporary_password = generate_password()

        # --------------------------------------------------
        # Create authentication user account
        # --------------------------------------------------
        new_user = User(
            email=doctor_data.email,
            password=hash_password(temporary_password),
            is_active=True,
        )

        db.add(new_user)
        db.flush()  # Ensure user_id is available for FK relation

        # --------------------------------------------------
        # Create doctor profile (clinical domain entity)
        # --------------------------------------------------
        new_doctor = Doctor(
            user_id=new_user.user_id,
            first_name=doctor_data.first_name,
            last_name=doctor_data.last_name,
            sex=doctor_data.sex,
            phone=doctor_data.phone,
            specialization=doctor_data.specialization,
            experience_years=doctor_data.experience_years,
            hospital=doctor_data.hospital,
            license_number=doctor_data.license_number,
            profile_image=doctor_data.profile_image, 
        )

        db.add(new_doctor)

        # --------------------------------------------------
        # Commit transaction
        # --------------------------------------------------
        db.commit()
        db.refresh(new_doctor)

        # --------------------------------------------------
        # Return created doctor + temporary credentials
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_201_CREATED,
            "detail": "Doctor registered successfully.",
            "data": {
                "email": new_user.email,
                "password": temporary_password,
            },
        }

    except HTTPException:
        # Rollback transaction for expected validation errors
        db.rollback()
        raise

    except SQLAlchemyError as e:
        # Rollback database transaction on DB failure
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    except Exception as e:
    # Catch unexpected system/runtime errors
        db.rollback()
        raise HTTPException(

             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail=str(e),
        )