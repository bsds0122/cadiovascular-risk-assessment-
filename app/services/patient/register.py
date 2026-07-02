from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.models.patients import Patient


# ==========================================================
# REGISTER PATIENT SERVICE
# ==========================================================
def register_patient(
    db: Session,
    patient_data,
    doctor_id: int,
):
    try:

        # ======================================================
        # CREATE PATIENT RECORD
        # ======================================================
        patient = Patient(
            doctor_id=doctor_id,
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            sex=patient_data.sex,
            phone_number=patient_data.phone_number,
            next_of_kin_number=patient_data.next_of_kin_number,
            date_of_diagnosis=patient_data.date_of_diagnosis,
            diabetes_type=patient_data.diabetes_type,
            region=patient_data.region,
            district=patient_data.district,
            traditional_authority=patient_data.traditional_authority,
            village=patient_data.village,
            profile_image=patient_data.profile_image,
        )

        # ======================================================
        # SAVE TO DATABASE
        # ======================================================
        db.add(patient)
        db.commit()
        db.refresh(patient)

        # ======================================================
        # SUCCESS RESPONSE
        # ======================================================
        return {
            "status_code": 201,
            "detail": "Patient registered successfully",
        
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )