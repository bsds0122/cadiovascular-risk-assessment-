from fastapi import (
    HTTPException,
    status,
    Depends
)
from app.dependencies.auth import get_current_user


def get_real_admin_id(current_user: dict = Depends(get_current_user)) -> int:
    """
    Dependency to get the authenticated administrator ID.
    Ensures the user has the 'administrator' role.
    """
    if current_user.get("role") != "administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is restricted to administrators."
        )

    return int(current_user.get("id"))
