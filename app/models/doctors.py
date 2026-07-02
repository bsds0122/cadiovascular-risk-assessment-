from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ==========================================================
# DOCTOR PROFILE AND HEALTHCARE MANAGEMENT MODEL
# ==========================================================
class Doctor(Base):
    """
    Represents a healthcare professional registered in the system.

    Stores the doctor's personal information, professional
    credentials, workplace details, and links to the user
    account used for system authentication.
    """

    # ------------------------------------------------------
    # Database table configuration
    # ------------------------------------------------------
    __tablename__ = "doctors"

    # ------------------------------------------------------
    # Primary key: Unique identifier for each doctor
    # ------------------------------------------------------
    doctor_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ------------------------------------------------------
    # Foreign key linking the doctor profile to a unique
    # user account used for authentication and system access
    # ------------------------------------------------------
    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False,
    )

    # ------------------------------------------------------
    # Doctor personal identification details
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
    # Doctor contact information
    # ------------------------------------------------------
    phone = Column(
        String(20),
        nullable=False,
    )

    # ------------------------------------------------------
    # Doctor professional qualifications and experience
    # ------------------------------------------------------
    specialization = Column(
        String(100),
        nullable=False,
    )

    experience_years = Column(
        Integer,
        nullable=False,
    )

    # ------------------------------------------------------
    # Healthcare facility where the doctor provides services
    # ------------------------------------------------------
    hospital = Column(
        String(255),
        nullable=False,
    )

    # ------------------------------------------------------
    # Official medical license number
    # Must be unique for each registered doctor
    # ------------------------------------------------------
    license_number = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    # ------------------------------------------------------
    # Optional profile image URL or storage file path
    # ------------------------------------------------------
    profile_image = Column(
        String(255),
        nullable=True,
    )

    # ------------------------------------------------------
    # Relationship with the authentication user account
    # Each doctor has one associated user account containing
    # login credentials and access permissions
    # ------------------------------------------------------
    user = relationship(
        "User",
        back_populates="doctor",
    )

    # ------------------------------------------------------
    # Relationship with patients under the doctor's care
    # A doctor can manage multiple patients
    # Deleting a doctor  could not removes all associated patient records
    # ------------------------------------------------------
    patients = relationship(
        "Patient",
        back_populates="doctor",
      
    )