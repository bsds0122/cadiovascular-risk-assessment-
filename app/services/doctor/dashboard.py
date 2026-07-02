from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.doctors import Doctor
from app.models.patients import Patient
from app.models.assessments import Assessment


# ==========================================================
# GREETING HELPER
# ==========================================================
def get_greeting():
    hour = datetime.now(ZoneInfo("Africa/Blantyre")).hour

    if 0 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"


# ==========================================================
# DASHBOARD SERVICE
# ==========================================================
def get_dashboard_data(db: Session, current_doctor: int):

    # ======================================================
    # DOCTOR
    # ======================================================
    doctor = (
        db.query(Doctor)
        .filter(Doctor.doctor_id == current_doctor)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    doctor_name = f"{doctor.first_name} {doctor.last_name}"

    # ======================================================
    # PATIENTS
    # ======================================================
    patients = db.query(Patient).all()
    total_patients = len(patients)

    total_men = len([
        p for p in patients
        if p.sex and p.sex.lower() == "male"
    ])

    total_women = len([
        p for p in patients
        if p.sex and p.sex.lower() == "female"
    ])

    patient_overview_stats = [
        {"title": "Total Patients", "value": total_patients, "type": "total"},
        {"title": "Total Men", "value": total_men, "type": "male"},
        {"title": "Total Women", "value": total_women, "type": "female"},
    ]

    # ======================================================
    # DIABETES TYPE DISTRIBUTION
    # ======================================================
    diabetes_types = ["Type 1", "Type 2", "Gestational"]

    valid_patients = (
        db.query(Patient)
        .filter(Patient.diabetes_type.in_(diabetes_types))
        .all()
    )

    total_valid = len(valid_patients)

    diabetes_type_stats = []

    for diabetes_type in diabetes_types:

        male_count = (
            db.query(Patient)
            .filter(
                Patient.diabetes_type == diabetes_type,
                Patient.sex.ilike("male")
            )
            .count()
        )

        female_count = (
            db.query(Patient)
            .filter(
                Patient.diabetes_type == diabetes_type,
                Patient.sex.ilike("female")
            )
            .count()
        )

        total = male_count + female_count

        percentage = (
            round((total / total_valid) * 100, 1)
            if total_valid > 0
            else 0
        )

        diabetes_type_stats.append({
            "type": diabetes_type,
            "male": male_count,
            "female": female_count,
            "percentage": f"{percentage}%"
        })

    # ======================================================
    # ASSESSMENTS / RISK LEVELS (MATCH MODEL EXACTLY)
    # ======================================================
    assessments = db.query(Assessment).all()
    total_assessments = len(assessments)

    risk_counts = {
        "Low Risk": 0,
        "Medium Risk": 0,
        "High Risk": 0,
        "Very High Risk": 0
    }

    for assessment in assessments:

        if not assessment.risk_level:
            continue

        risk_level = assessment.risk_level.strip()

        if risk_level in risk_counts:
            risk_counts[risk_level] += 1

    risk_level_stats = []

    for level in [
        "Low Risk",
        "Medium Risk",
        "High Risk",
        "Very High Risk"
    ]:

        count = risk_counts[level]

        percentage = (
            round((count / total_assessments) * 100, 1)
            if total_assessments > 0
            else 0
        )

        risk_level_stats.append({
            "level": level,
            "count": count,
            "percentage": f"{percentage}%"
        })

    # ======================================================
    # RESPONSE
    # ======================================================
    return {
        "status_code": 200,
        "status": "success",
        "detail": "Dashboard statistics fetched successfully",
        "data": {
            "greeting": get_greeting(),
            "doctor_name": doctor_name,
            "patientOverviewStats": patient_overview_stats,
            "diabetesTypeStats": diabetes_type_stats,
            "totalAssessments": total_assessments,
            "riskLevelStats": risk_level_stats
        }
    }