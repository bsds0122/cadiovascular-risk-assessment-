from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.models.administrator import Administrator
from app.utils.security import hash_password
from app.schemas.admin.register import AdminRegister


def register_admin(
    db: Session,
    admin_data: AdminRegister,
):
    """
    Register a new administrator account and profile.

    Process:
    1. Validate that email is not already in use
    2. Generate a secure temporary password
    3. Create a User record (authentication layer)
    4. Create an Administrator profile linked to the User
    5. Commit both records to the database
    """

    try:
        # ----------------------------------------------------------
        # CHECK IF EMAIL ALREADY EXISTS
        # Prevent duplicate administrator accounts using same email
        # ----------------------------------------------------------
        existing_user = (
            db.query(User)
            .filter(User.email == admin_data.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An account with this email address already exists. "
                    "Please use a different email address."
                ),
            )

        # ----------------------------------------------------------
        # GENERATE TEMPORARY PASSWORD
        # This password should be changed after first login
        # ----------------------------------------------------------
        temporary_password = token_urlsafe(8)

        # ----------------------------------------------------------
        # CREATE USER ACCOUNT (AUTH LAYER)
        # This stores login credentials for the administrator
        # ----------------------------------------------------------
        new_user = User(
            email=admin_data.email,
            password=hash_password(temporary_password),
            is_active=True,
        )

        db.add(new_user)

        # Flush to generate user_id before creating linked profile
        # (required for foreign key relationship)
        db.flush()

        # ----------------------------------------------------------
        # CREATE ADMINISTRATOR PROFILE
        # Stores personal and professional details of the admin
        # ----------------------------------------------------------
        new_admin = Administrator(
            user_id=new_user.user_id,
            first_name=admin_data.first_name,
            last_name=admin_data.last_name,
            phone=admin_data.phone,
            experience_years=admin_data.experience_years,
            hospital=admin_data.hospital,
            profile_image=admin_data.profile_image,
        )

        db.add(new_admin)

        # ----------------------------------------------------------
        # SAVE TO DATABASE
        # Commits both User and Administrator records together
        # ----------------------------------------------------------
        db.commit()

        # Refresh objects to get updated DB values
        db.refresh(new_user)
        db.refresh(new_admin)

        # ----------------------------------------------------------
        # RETURN RESPONSE
        # Includes generated temporary password for first login
        # ----------------------------------------------------------
        return {
            "status_code": status.HTTP_201_CREATED,
            "detail": "Administrator account created successfully.",
            "data": {
                "email": new_user.email,
                "password": temporary_password,
            },
        }

    except HTTPException:
        # Re-raise known HTTP errors without modification
        db.rollback()
        raise

    except SQLAlchemyError:
        # Handle database-related failures (constraint issues, connection errors)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to create administrator account at this time."
            ),
        )

    except Exception:
        # Catch-all for unexpected runtime errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Something went wrong while creating the administrator "
                "account. Please try again later."
            ),
        )