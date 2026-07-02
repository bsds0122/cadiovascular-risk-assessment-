from fastapi import (
    Depends,  HTTPException
)
from app.dependencies.auth import get_current_user


def get_current_doctor_user(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "doctor":
        raise HTTPException(status_code=403, detail="Doctors only")

    doctor_id = current_user.get("doctor_id")

    if not doctor_id:
        raise HTTPException(status_code=401, detail="Missing doctor_id")

    return doctor_id


