from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.assessments import Assessment



def get_patient_monthly_monitoring(db: Session, patient_id: int, year: int):
    
    try:

        results = (
            db.query(
                Assessment.assessment_month.label("month"),
                func.count(Assessment.patient_id).label("number_of_visits"),
                func.avg(Assessment.systolic_bp).label("average_systolic_bp"),
                func.avg(Assessment.diastolic_bp).label("average_diastolic_bp"),
                func.avg(Assessment.glucose).label("average_glucose"),
            )
            .filter(
                Assessment.patient_id == patient_id,
                Assessment.assessment_year == year,
            )
            .group_by(Assessment.assessment_month)
            .order_by(Assessment.assessment_month)
            .all()
        )

        if not results:
            return {
                "status_code": 404,
                "detail": "No monitoring records found",
                "data": []
            }

        data = [
            {
                "month": r.month,
                "number_of_visits": r.number_of_visits,
                "average_systolic_bp": round(float(r.average_systolic_bp), 2),
                "average_diastolic_bp": round(float(r.average_diastolic_bp), 2),
                "average_glucose": round(float(r.average_glucose), 2),
            }
            for r in results
        ]

        return {
            "status_code": 200,
            "detail": "Monitoring data retrieved successfully",
            "data": data
        }

    except Exception as e:
        return {
            "status_code": 500,
            "detail": str(e),
            "data": None
        }