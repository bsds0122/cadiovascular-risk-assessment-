from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import status

from app.models.patients import Patient


# ==========================================================
# SERIALIZERS
# ==========================================================
def patient_summary_to_dict(patient):
    return {
        "patient_id": patient.patient_id,
        "first_name": patient.first_name or "",
        "last_name": patient.last_name or "",
        "patient_image": patient.profile_image,
    }


def patient_to_dict(patient):
    return {
        "patient_id": patient.patient_id,
        "first_name": patient.first_name or "",
        "last_name": patient.last_name or "",
        "sex": patient.sex,
        "phone_number": patient.phone_number,
        "next_of_kin_number": patient.next_of_kin_number,
        "date_of_diagnosis": patient.date_of_diagnosis,
        "diabetes_type": patient.diabetes_type,
        "district": patient.district,
        "region": patient.region,
        "traditional_authority": patient.traditional_authority,
        "village": patient.village,
        "patient_image": patient.profile_image,
    }


# ==========================================================
# GET ALL PATIENTS
# ==========================================================
def get_all_patients(
    db: Session,
    skip: int = 0,
    limit: int = 15
):
    try:
        if skip < 0:
            skip = 0

        if limit < 1:
            limit = 10

        patients = (
            db.query(Patient)
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Patients retrieved successfully",
            "data": [patient_summary_to_dict(p) for p in patients],
        }

    except Exception:
        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Database error while retrieving patients",
            "data": [],
        }


# ==========================================================
# SEARCH PATIENTS
# ==========================================================
def search_patients(
    db: Session,
    name: str,
    limit: int = 10
):
    try:
        if not name:
            return {
                "status_code": status.HTTP_200_OK,
                "detail": "Empty search query",
                "data": [],
            }

        search_term = " ".join(name.strip().lower().split())

        patients = (
            db.query(Patient)
            .filter(
                or_(
                    func.lower(Patient.first_name).like(f"{search_term}%"),
                    func.lower(Patient.last_name).like(f"{search_term}%"),
                    func.lower(Patient.first_name).like(f"%{search_term}%"),
                    func.lower(Patient.last_name).like(f"%{search_term}%"),
                )
            )
            .limit(limit)
            .all()
        )

        def safe(value):
            return (value or "").lower()

        def score(patient):
            first = safe(patient.first_name)
            last = safe(patient.last_name)
            full = f"{first} {last}"

            score = 0

            if full == search_term:
                score += 100

            if first.startswith(search_term):
                score += 50

            if last.startswith(search_term):
                score += 50

            if search_term in full:
                score += 20

            return -score

        patients.sort(key=score)

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Search completed successfully",
            "data": [patient_summary_to_dict(p) for p in patients],
        }

    except Exception:
        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Search failed",
            "data": [],
        }


# ==========================================================
# AUTOCOMPLETE PATIENTS
# ==========================================================
def autocomplete_patients(
    db: Session,
    query: str,
    limit: int = 10
):
    try:
        if not query:
            return {
                "status_code": status.HTTP_200_OK,
                "detail": "Empty query",
                "data": [],
            }

        q = " ".join(query.strip().lower().split())

        patients = (
            db.query(Patient)
            .filter(
                or_(
                    func.lower(Patient.first_name).like(f"{q}%"),
                    func.lower(Patient.last_name).like(f"{q}%"),
                    func.lower(Patient.first_name).like(f"%{q}%"),
                    func.lower(Patient.last_name).like(f"%{q}%"),
                )
            )
            .limit(limit)
            .all()
        )

        def safe(value):
            return (value or "").lower()

        def score(patient):
            first = safe(patient.first_name)
            last = safe(patient.last_name)
            full = f"{first} {last}"

            if full == q:
                return 0

            if first.startswith(q):
                return 1

            if last.startswith(q):
                return 1

            if q in full:
                return 2

            return 3

        patients.sort(key=score)

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Autocomplete successful",
            "data": [
                {
                    "patient_id": p.patient_id,
                    "label": f"{p.first_name or ''} {p.last_name or ''}".strip(),
                    "image": p.profile_image,
                }
                for p in patients
            ],
        }

    except Exception:
        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Autocomplete failed",
            "data": [],
        }


# ==========================================================
# GET SINGLE PATIENT
# ==========================================================
def get_patient_by_id(
    db: Session,
    patient_id: int
):
    try:
        patient = (
            db.query(Patient)
            .filter(Patient.patient_id == patient_id)
            .first()
        )

        if not patient:
            return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "detail": "Patient not found",
                "data": None,
            }

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Patient retrieved successfully",
            "data": patient_to_dict(patient),
        }

    except Exception:
        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": "Failed to fetch patient",
            "data": None,
        }
    


# ==========================================================
# UPDATE PATIENT
# ==========================================================

def update_patient(
    db: Session,
    patient_id: int,
    doctor_id: int,
    update_data: dict,
):
    try:

        patient = (
            db.query(Patient)
            .filter(Patient.patient_id == patient_id)
            .first()
        )

        if not patient:
            return {
                "status_code": status.HTTP_404_NOT_FOUND,
                "detail": "Patient not found",
                "data": None,
            }

        if patient.doctor_id != doctor_id:
            return {
                "status_code": status.HTTP_403_FORBIDDEN,
                "detail": "You can only edit patients you registered",
                "data": None,
            }

        for field, value in update_data.items():
            if hasattr(patient, field):
                setattr(patient, field, value)

        db.commit()
        db.refresh(patient)

        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Patient updated successfully",
            "data": patient_to_dict(patient),
        }

    except Exception as e:
        db.rollback()

        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": str(e),
            "data": None,
        }








































































