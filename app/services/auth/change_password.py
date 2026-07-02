from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.security import (
    verify_password,
    hash_password,
)


def change_password(
    db: Session,
    default_password: str,
    new_password: str,
):
    """
    Find user using temporary password and update it.
    """

    user_found = None

    users = db.query(User).all()

    for user in users:
        if verify_password(
            default_password,
            user.password
        ):
            user_found = user
            break

    if not user_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid default password",
        )

    user_found.password = hash_password(
        new_password
    )

    db.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "detail": "Password updated successfully",
        "data": {
            "email": user_found.email
        },
    }