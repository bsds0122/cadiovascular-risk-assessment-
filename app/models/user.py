from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


# ==========================================================
# USER AUTHENTICATION MODEL
# ==========================================================
class User(Base):
    """
    Represents a system user responsible for authentication
    and account access management.

    A user account can be associated with either:
    - A doctor profile
    - An administrator profile
    """

    # ------------------------------------------------------
    # Database table configuration
    # ------------------------------------------------------
    __tablename__ = "users"

    # ------------------------------------------------------
    # Primary key: Unique identifier for each user account
    # ------------------------------------------------------
    user_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ------------------------------------------------------
    # Unique email address used as the login identifier
    # ------------------------------------------------------
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------
    # Securely hashed password used for authentication
    # Plain text passwords should never be stored
    # ------------------------------------------------------
    password = Column(
        String(255),
        nullable=False,
    )

    # ------------------------------------------------------
    # Account activation status
    # Disabled users are prevented from accessing the system
    # ------------------------------------------------------
    is_active = Column(
        Boolean,
        default=True,
    )

    # ------------------------------------------------------
    # One-to-one relationship with a doctor profile
    # Deleting a user removes the associated doctor record
    # ------------------------------------------------------
    doctor = relationship(
        "Doctor",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------
    # One-to-one relationship with an administrator profile
    # Deleting a user removes the associated administrator record
    # ------------------------------------------------------
    administrator = relationship(
        "Administrator",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )