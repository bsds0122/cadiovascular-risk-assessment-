from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.administrator import Administrator
from app.models.doctors import Doctor
from app.models.patients import Patient
from app.models.assessments import Assessment


def get_time_based_greeting():
    """
    Generate a greeting message based on the current system time.

    Returns:
        str: "Good Morning", "Good Afternoon", or "Good Evening"
    """

    hour = datetime.now().hour

    # Morning: 00:00 - 11:59
    if hour < 12:
        return "Good Morning"

    # Afternoon: 12:00 - 16:59
    if hour < 17:
        return "Good Afternoon"

    # Evening: 17:00 - 23:59
    return "Good Evening"


def get_admin_dashboard_data(
    db: Session,
    admin_id: int,
):
    """
    Retrieve full administrator dashboard data.

    This includes:
    - Admin greeting message
    - Summary statistics (doctors, patients, assessments)
    - Gender-based distributions
    - Risk category distribution
    - Recent doctors and patients activity
    """

    try:
        # ----------------------------------------------------------
        # VALIDATE ADMIN EXISTS
        # Ensure the requesting administrator account is valid
        # ----------------------------------------------------------
        admin = (
            db.query(Administrator)
            .filter(Administrator.admin_id == admin_id)
            .first()
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrator profile not found.",
            )

        # ----------------------------------------------------------
        # GENERATE PERSONALIZED GREETING
        # Combines time-based greeting with admin's first name
        # ----------------------------------------------------------
        greeting = (
            f"{get_time_based_greeting()} {admin.first_name}"
        )

        # ----------------------------------------------------------
        # DOCTOR STATISTICS
        # Total doctors and gender breakdown
        # ----------------------------------------------------------
        total_doctors = db.query(Doctor).count()
        male_doctors = (
            db.query(Doctor)
            .filter(Doctor.sex == "Male")
            .count()
        )
        female_doctors = (
            db.query(Doctor)
            .filter(Doctor.sex == "Female")
            .count()
        )

        # ----------------------------------------------------------
        # PATIENT STATISTICS
        # Total patients and gender breakdown
        # ----------------------------------------------------------
        total_patients = db.query(Patient).count()
        male_patients = (
            db.query(Patient)
            .filter(Patient.sex == "Male")
            .count()
        )
        female_patients = (
            db.query(Patient)
            .filter(Patient.sex == "Female")
            .count()
        )

        # ----------------------------------------------------------
        # ASSESSMENT STATISTICS
        # Total assessments and risk category distribution
        # ----------------------------------------------------------
        total_assessments = db.query(Assessment).count()

        risk_distribution = [
            {
                "name": "Low Risk",
                "value": db.query(Assessment)
                .filter(Assessment.risk_category == "Low Risk")
                .count(),
            },
            {
                "name": "Moderate Risk",
                "value": db.query(Assessment)
                .filter(Assessment.risk_category == "Moderate Risk")
                .count(),
            },
            {
                "name": "High Risk",
                "value": db.query(Assessment)
                .filter(Assessment.risk_category == "High Risk")
                .count(),
            },
        ]

        # ----------------------------------------------------------
        # RECENT ACTIVITY
        # Fetch latest registered doctors and patients
        # ----------------------------------------------------------
        recent_doctors = (
            db.query(Doctor)
            .order_by(Doctor.doctor_id.desc())
            .limit(5)
            .all()
        )

        recent_patients = (
            db.query(Patient)
            .order_by(Patient.patient_id.desc())
            .limit(5)
            .all()
        )

        # ----------------------------------------------------------
        # RESPONSE STRUCTURE
        # Organize dashboard data into frontend-friendly format
        # ----------------------------------------------------------
        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Dashboard loaded successfully.",
            "data": {
                "greeting": greeting,
                "summary": {
                    "total_doctors": total_doctors,
                    "total_patients": total_patients,
                    "total_assessments": total_assessments,
                },
                "statistics": {
                    "doctors": {
                        "male": male_doctors,
                        "female": female_doctors,
                    },
                    "patients": {
                        "male": male_patients,
                        "female": female_patients,
                    },
                    "assessments": {
                        "risk_distribution": risk_distribution,
                    },
                },
                "recent_activity": {
                    "doctors": [
                        {
                            "id": doctor.doctor_id,
                            "name": f"{doctor.first_name} {doctor.last_name}",
                            "specialization": doctor.specialization,
                            "hospital": doctor.hospital,
                        }
                        for doctor in recent_doctors
                    ],
                    "patients": [
                        {
                            "id": patient.patient_id,
                            "name": f"{patient.first_name} {patient.last_name}",
                            "diabetes_type": patient.diabetes_type,
                        }
                        for patient in recent_patients
                    ],
                },
            },
        }

    except HTTPException:
        # Re-raise known HTTP errors without modification
        raise

    except SQLAlchemyError:
        # Handle database-related errors (queries, connections, etc.)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to load dashboard.",
        )

    except Exception:
        # Catch-all for unexpected runtime errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again.",
        )