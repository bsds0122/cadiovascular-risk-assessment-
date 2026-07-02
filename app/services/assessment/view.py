from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.models.assessments import Assessment


def get_assessments_by_date(
    db: Session,
    patient_id: int,
    year: int,
    month: int,
    day: int,
):
    try:

        assessments = (
            db.query(Assessment)
            .filter(
                Assessment.patient_id == patient_id,
                Assessment.assessment_year == year,
                Assessment.assessment_month == month,
                Assessment.assessment_day == day,
            )
            .all()   # 👈 important change
        )

        if not assessments:
            return {
                "status_code": 404,
                "details": "No assessments found for this date",
                "data": []
            }

        return {
            "status_code": 200,
            "details": "Assessments retrieved successfully",
            "data": [
                {
                    "risk_level": a.risk_level,
                    "risk_percentage": a.risk_percentage,
                    "feature_importance": a.feature_importance,
                    
                }
                for a in assessments
            ]
        }

    except SQLAlchemyError as e:
        return {
            "status_code": 500,
            "details": f"Error retrieving assessments: {str(e)}",
            "data": None
        }