import io
import logging

import pandas as pd
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.patients import Patient
from app.schemas.patient.register import PatientRegister


# ==========================================================
# LOGGER SETUP
# ==========================================================
logger = logging.getLogger(__name__)


# ==========================================================
# LOAD CSV / EXCEL FILE
# ==========================================================
def load_dataframe(file: UploadFile) -> pd.DataFrame:
    """
    Read uploaded CSV or Excel file.
    """

    filename = file.filename.lower()

    try:
        content = file.file.read()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        if filename.endswith(".csv"):
            dataframe = pd.read_csv(io.BytesIO(content))

        elif filename.endswith((".xlsx", ".xls")):
            dataframe = pd.read_excel(io.BytesIO(content))

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV or Excel files are supported.",
            )

        # Remove completely empty rows
        dataframe.dropna(how="all", inplace=True)

        return dataframe

    except HTTPException:
        raise

    except Exception as error:
        logger.error(f"File parsing error: {error}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file.",
        )


# ==========================================================
# BULK PATIENT REGISTRATION
# ==========================================================
def register_patients_excel(
    db: Session,
    file: UploadFile,
    doctor_id: int,
):
    """
    Register multiple patients from CSV or Excel.
    """

    try:
        # --------------------------------------------------
        # LOAD FILE
        # --------------------------------------------------
        dataframe = load_dataframe(file)

        if dataframe.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No patient records found in file.",
            )

        # --------------------------------------------------
        # VALIDATE REQUIRED COLUMNS
        # --------------------------------------------------
        required_columns = [
            "first_name",
            "last_name",
            "sex",
            "phone_number",
            "next_of_kin_number",
            "date_of_diagnosis",
            "diabetes_type",
            "region",
            "district",
            "traditional_authority",
            "village",
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}",
            )

        # --------------------------------------------------
        # STORAGE LISTS
        # --------------------------------------------------
        patients_to_save = []
        failed_records = []

        # Track duplicates inside the same uploaded file
        uploaded_phone_numbers = set()

        # --------------------------------------------------
        # PROCESS EACH EXCEL ROW
        # --------------------------------------------------
        for row_number, row in enumerate(
            dataframe.to_dict(orient="records"),
            start=2,
        ):
            try:
                # ------------------------------------------
                # Clean data
                # ------------------------------------------
                patient_data = {
                    key: (
                        str(value).strip()
                        if pd.notnull(value)
                        else None
                    )
                    for key, value in row.items()
                }

                # ------------------------------------------
                # Convert diagnosis date
                # ------------------------------------------
                if patient_data.get("date_of_diagnosis"):
                    patient_data["date_of_diagnosis"] = (
                        pd.to_datetime(
                            patient_data["date_of_diagnosis"]
                        ).date()
                    )

                # ------------------------------------------
                # Validate schema
                # ------------------------------------------
                patient_schema = PatientRegister(
                    **patient_data
                )

                # ------------------------------------------
                # Check duplicate in uploaded file
                # ------------------------------------------
                # if (
                    # patient_schema.phone_number
                    # in uploaded_phone_numbers
                # ):
                    # raise ValueError(
                        # "Duplicate phone number in uploaded file."
                    # )

                # uploaded_phone_numbers.add(
                    # patient_schema.phone_number
                # )

                # ------------------------------------------
                # Check duplicate in database
                # ------------------------------------------
                # existing_patient = (
                    # db.query(Patient)
                    # .filter(
                        # Patient.phone_number
                        # == patient_schema.phone_number
                    # )
                    # .first()
                # )

                # if existing_patient:
                    # raise ValueError(
                        # "Patient with this phone number already exists."
                    # )

                # ------------------------------------------
                # Create patient object
                # ------------------------------------------
                new_patient = Patient(
                    doctor_id=doctor_id,
                    first_name=patient_schema.first_name,
                    last_name=patient_schema.last_name,
                    sex=patient_schema.sex,
                    phone_number=patient_schema.phone_number,
                    next_of_kin_number=(
                        patient_schema.next_of_kin_number
                    ),
                    date_of_diagnosis=(
                        patient_schema.date_of_diagnosis
                    ),
                    diabetes_type=patient_schema.diabetes_type,
                    region=patient_schema.region,
                    district=patient_schema.district,
                    traditional_authority=(
                        patient_schema.traditional_authority
                    ),
                    village=patient_schema.village,
                    profile_image=patient_schema.profile_image,
                )

                # ------------------------------------------
                # Add to bulk save list
                # ------------------------------------------
                patients_to_save.append(
                    new_patient
                )

            # ----------------------------------------------
            # Capture row errors and continue
            # ----------------------------------------------
            except Exception as error:

                logger.error(
                    f"Error processing row {row_number}: {error}"
                )

                failed_records.append(
                    {
                        "excel_row": row_number,
                        "phone_number": row.get(
                            "phone_number"
                        ),
                        "error": str(error),
                    }
                )

        # --------------------------------------------------
        # SAVE ALL VALID PATIENTS
        # --------------------------------------------------
        if patients_to_save:
            db.add_all(patients_to_save)
            db.commit()

        # --------------------------------------------------
        # RETURN SUMMARY
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_201_CREATED,
            "detail": (
                "Patient file processed successfully."
            ),
            "data": {
                "total_records": len(dataframe),
                "successful_registrations": (
                    len(patients_to_save)
                ),
                "failed_registrations": (
                    len(failed_records)
                ),
                "failed_records": failed_records,
            },
        }

    # ------------------------------------------------------
    # KNOWN HTTP ERRORS
    # ------------------------------------------------------
    except HTTPException:
        raise

    # ------------------------------------------------------
    # DATABASE ERRORS
    # ------------------------------------------------------
    except SQLAlchemyError as error:

        db.rollback()

        logger.error(
            f"Database error: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save patient records.",
        )

    # ------------------------------------------------------
    # UNEXPECTED ERRORS
    # ------------------------------------------------------
    except Exception as error:

        db.rollback()

        logger.error(
            f"Unexpected bulk registration error: {error}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unexpected error occurred during patient registration."
            ),
        )