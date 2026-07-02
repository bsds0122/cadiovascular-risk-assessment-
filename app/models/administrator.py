from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


# ==========================================================
# ADMINISTRATOR PROFILE MODEL
# ==========================================================
class Administrator(Base):
    """
    Represents an administrator responsible for managing
    the healthcare system.

    Stores administrator personal information, professional
    details, and links to the authentication user account.
    """

    # ------------------------------------------------------
    # Database table configuration
    # ------------------------------------------------------
    __tablename__ = "administrators"

    # ------------------------------------------------------
    # Primary key: Unique identifier for each administrator
    # ------------------------------------------------------
    admin_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ------------------------------------------------------
    # Foreign key linking the administrator profile to a
    # unique user account used for system authentication
    # ------------------------------------------------------
    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False,
    )

    # ------------------------------------------------------
    # Administrator personal identification details
    # ------------------------------------------------------
    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    # ------------------------------------------------------
    # Administrator contact information
    # ------------------------------------------------------
    phone = Column(
        String(20),
        nullable=True,
    )

    # ------------------------------------------------------
    # Administrator professional and workplace information
    # ------------------------------------------------------
    experience_years = Column(
        Integer,
        nullable=True,
    )

    hospital = Column(
        String(255),
        nullable=True,
    )

    # ------------------------------------------------------
    # Optional profile image URL or file storage path
    # ------------------------------------------------------
    profile_image = Column(
        String(500),
        nullable=True,
    )

    # ------------------------------------------------------
    # Relationship with the authentication user account
    # Each administrator has exactly one associated user
    # account containing login credentials
    # ------------------------------------------------------
    user = relationship(
        "User",
        back_populates="administrator",
    )