from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.models.administrator import Administrator
from app.schemas.admin.update import AdministratorProfileUpdate


# ==========================================================
# ADMIN SERIALIZATION HELPER
# ==========================================================
def admin_to_dict(admin: Administrator) -> dict:
    """
    Convert Administrator ORM model into API response format.
    Used for consistent output formatting.
    """

    return {
        "admin_id": admin.admin_id,
        "first_name": admin.first_name,
        "last_name": admin.last_name,
        "phone": admin.phone,
        "experience_years": admin.experience_years,
        "hospital": admin.hospital,
        "profile_image": admin.profile_image,
        "email": admin.user.email if admin.user else None,
    }


# ==========================================================
# GET ADMIN PROFILE
# ==========================================================
def get_admin_profile(
    db: Session,
    admin_id: int,
):
    """
    Retrieve administrator profile information
    including linked user account details.
    """

    try:
        # --------------------------------------------------
        # Fetch administrator with user relationship
        # --------------------------------------------------
        admin = (
            db.query(Administrator)
            .options(joinedload(Administrator.user))
            .filter(Administrator.admin_id == admin_id)
            .first()
        )

        # --------------------------------------------------
        # Validate existence
        # --------------------------------------------------
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrator profile not found.",
            )

        # --------------------------------------------------
        # Return formatted response
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Administrator profile retrieved successfully.",
            "data": admin_to_dict(admin),
        }

    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve administrator profile.",
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )


# ==========================================================
# UPDATE ADMIN PROFILE
# ==========================================================
def update_admin_profile(
    db: Session,
    admin_id: int,
    profile_data: AdministratorProfileUpdate,
):
    """
    Update administrator profile using provided fields only.
    Supports partial updates (PATCH behavior).
    """

    try:
        # --------------------------------------------------
        # Fetch administrator record
        # --------------------------------------------------
        admin = (
            db.query(Administrator)
            .options(joinedload(Administrator.user))
            .filter(Administrator.admin_id == admin_id)
            .first()
        )

        # --------------------------------------------------
        # Validate existence
        # --------------------------------------------------
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Administrator profile not found.",
            )

        # --------------------------------------------------
        # Extract only provided fields
        # --------------------------------------------------
        update_data = profile_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No information provided for update.",
            )

        # --------------------------------------------------
        # Apply updates dynamically
        # --------------------------------------------------
        for field, value in update_data.items():
            setattr(admin, field, value)

        # --------------------------------------------------
        # Commit changes
        # --------------------------------------------------
        db.commit()
        db.refresh(admin)

        # --------------------------------------------------
        # Return updated profile
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Administrator profile updated successfully.",
            "data": admin_to_dict(admin),
        }

    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update administrator profile.",
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again later.",
        )