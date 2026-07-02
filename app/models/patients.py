from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ==========================================================
# PATIENT INFORMATION AND MEDICAL RECORD MODEL
# ==========================================================
class Patient(Base):
    """
    Represents a patient registered under a doctor's care.

    Stores the patient's personal details, contact information,
    diabetes diagnosis data, residential location, and links
    to clinical assessment records.
    """

    # ------------------------------------------------------
    # Database table configuration
    # ------------------------------------------------------
    __tablename__ = "patients"

    # ------------------------------------------------------
    # Primary key: Unique identifier for each patient
    # ------------------------------------------------------
    patient_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ------------------------------------------------------
    # Foreign key linking the patient to the assigned doctor
    # ------------------------------------------------------
    doctor_id = Column(
        Integer,
        ForeignKey("doctors.doctor_id"),
        nullable=False,
    )

    # ------------------------------------------------------
    # Patient personal identification details
    # ------------------------------------------------------
    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    sex = Column(
        String(10),
        nullable=False,
        default="Male",
    )


    # ------------------------------------------------------
    # Patient and emergency contact information
    # ------------------------------------------------------
    phone_number = Column(
        String(20),
        nullable=False,
    )

    next_of_kin_number = Column(
        String(20),
        nullable=False,
    )

    # ------------------------------------------------------
    # Diabetes diagnosis and medical classification
    # ------------------------------------------------------
    date_of_diagnosis = Column(
        Date,
        nullable=False,
    )

    diabetes_type = Column(
        String(50),
        nullable=False,
    )

    # ------------------------------------------------------
    # Patient residential location information
    # ------------------------------------------------------
    region = Column(
        String(100),
        nullable=False,
    )

    district = Column(
        String(100),
        nullable=False,
    )

    traditional_authority = Column(
        String(100),
        nullable=False,
    )

    village = Column(
        String(100),
        nullable=False,
    )

    # ------------------------------------------------------
    # Optional patient profile image path or URL
    # ------------------------------------------------------
    profile_image = Column(
        String(255),
        nullable=True,
    )

    # ------------------------------------------------------
    # Record creation timestamp for patient registration
    # ------------------------------------------------------
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------
    # Relationship with the doctor responsible for the patient
    # ------------------------------------------------------
    doctor = relationship(
        "Doctor",
        back_populates="patients",
    )

    # ------------------------------------------------------
    # Relationship with all patient cardiovascular assessments
    # Deleting a patient also removes related assessments
    # ------------------------------------------------------
    assessments = relationship(
        "Assessment",
        back_populates="patient",
    )