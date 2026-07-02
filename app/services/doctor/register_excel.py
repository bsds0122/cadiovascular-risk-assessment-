import io
import secrets
import string

import pandas as pd

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.models.doctors import Doctor
from app.utils.security import hash_password


# ==========================================================
# TEMPORARY PASSWORD GENERATION (SECURE RANDOM CREDENTIALS)
# ==========================================================
def generate_password(length: int = 10) -> str:
    """
    Generate a secure temporary password for newly created doctor accounts.
    Used during bulk registration from Excel files.
    """

    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


# ==========================================================
# BULK DOCTOR REGISTRATION (EXCEL IMPORT)
# ==========================================================
def register_doctors_excel(
    db: Session,
    file: UploadFile,
):
    """
    Register multiple doctor accounts from an uploaded Excel file.

    Workflow:
    - Validate file format
    - Read and parse Excel data
    - Validate required fields
    - Check duplicates (email, license number)
    - Create User + Doctor records
    - Return success/failure summary
    """

    try:
        # --------------------------------------------------
        # Validate file type (Excel only)
        # --------------------------------------------------
        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Upload a valid Excel file.",
            )

        # --------------------------------------------------
        # Read file content into memory
        # --------------------------------------------------
        content = file.file.read()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        dataframe = pd.read_excel(io.BytesIO(content))

        # --------------------------------------------------
        # Validate dataset is not empty
        # --------------------------------------------------
        if dataframe.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No doctor records found.",
            )

        # --------------------------------------------------
        # Required Excel columns validation
        # --------------------------------------------------
        required_columns = [
            "first_name",
            "last_name",
            "sex",
            "email",
            "phone",
            "specialization",
            "experience_years",
            "hospital",
            "license_number",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing columns: {', '.join(missing_columns)}",
            )

        # --------------------------------------------------
        # Tracking results
        # --------------------------------------------------
        successful_accounts = []
        failed_records = []

        # ==================================================
        # PROCESS EACH DOCTOR ROW
        # ==================================================
        for index, row in dataframe.iterrows():

            try:
                email = str(row["email"]).strip()

                # --------------------------------------------------
                # Prevent duplicate user email registration
                # --------------------------------------------------
                if db.query(User).filter(User.email == email).first():
                    failed_records.append({
                        "row": index + 2,
                        "reason": "Email already exists.",
                    })
                    continue

                # --------------------------------------------------
                # Prevent duplicate medical license numbers
                # --------------------------------------------------
                if db.query(Doctor).filter(
                    Doctor.license_number == str(row["license_number"]).strip()
                ).first():
                    failed_records.append({
                        "row": index + 2,
                        "reason": "License already exists.",
                    })
                    continue

                # --------------------------------------------------
                # Generate secure temporary password
                # --------------------------------------------------
                temporary_password = generate_password()

                # --------------------------------------------------
                # Create user account (authentication layer)
                # --------------------------------------------------
                user = User(
                    email=email,
                    password=hash_password(temporary_password),
                    is_active=True,
                )

                db.add(user)
                db.flush()  # Get user_id before commit

                # --------------------------------------------------
                # Create doctor profile (domain layer)
                # --------------------------------------------------
                doctor = Doctor(
                    user_id=user.user_id,
                    first_name=str(row["first_name"]).strip(),
                    last_name=str(row["last_name"]).strip(),
                    sex=str(row["sex"]).strip(),
                    phone=str(row["phone"]).strip(),
                    specialization=str(row["specialization"]).strip(),
                    experience_years=int(row["experience_years"]),
                    hospital=str(row["hospital"]).strip(),
                    license_number=str(row["license_number"]).strip(),
                )

                db.add(doctor)

                # --------------------------------------------------
                # Store credentials for response/output
                # --------------------------------------------------
                successful_accounts.append({
                    "email": email,
                    "temporary_password": temporary_password,
                })

            except Exception:
                # Capture row-level processing errors without stopping batch
                failed_records.append({
                    "row": index + 2,
                    "reason": "Invalid doctor information.",
                })

        # --------------------------------------------------
        # Commit all valid records in bulk
        # --------------------------------------------------
        db.commit()

        # --------------------------------------------------
        # FINAL RESPONSE SUMMARY
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_201_CREATED,
            "detail": "Doctor registration completed.",
            "data": {
                "total_records": len(dataframe),
                "successful_registrations": len(successful_accounts),
                "failed_records": len(failed_records),
            },
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        # Rollback database transaction on failure
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while saving doctor records.",
        )

    except Exception:
        # Catch unexpected system errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while processing Excel file.",
        )