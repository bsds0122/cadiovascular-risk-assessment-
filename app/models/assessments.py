from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Assessment(Base):

    __tablename__ = "assessments"

    # ======================================================
    # PRIMARY KEY
    # ======================================================
    assessment_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ======================================================
    # FOREIGN KEY
    # ======================================================
    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id"),
        nullable=False,
        index=True,
    )

    # ======================================================
    # DATE OF ASSESSMENT
    # ======================================================
    assessment_year = Column(
        Integer,
        nullable=False,
        index=True,
    )

    assessment_month = Column(
        Integer,
        nullable=False,
        index=True,
    )

    assessment_day = Column(
        Integer,
        nullable=False,
        index=True,
    )

    # ======================================================
    # CLINICAL INPUTS USED FOR PREDICTION
    # ======================================================
    systolic_bp = Column(
        Integer,
        nullable=False,
    )

    diastolic_bp = Column(
        Integer,
        nullable=False,
    )

    glucose = Column(
        Float,
        nullable=False,
    )


    # ======================================================
    # MODEL OUTPUTS
    # ======================================================
    risk_level = Column(
        String(50),
        nullable=False,
        index=True,
    )

    risk_percentage = Column(
        Float,
        nullable=False,
    )

    # ======================================================
    # SHAP / FEATURE IMPORTANCE
    # Example:
    # [
    #   {
    #     "feature": "age",
    #     "effect": "Decrease Risk",
    #     "impact_percentage": 41.77
    #   }
    # ]
    # ======================================================
    feature_importance = Column(
        JSON,
        nullable=True,
    )

    # ======================================================
    # RELATIONSHIP
    # ======================================================
    patient = relationship(
        "Patient",
        back_populates="assessments",
    )