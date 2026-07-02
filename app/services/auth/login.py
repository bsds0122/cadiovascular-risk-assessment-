from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.doctors import Doctor
from app.models.administrator import Administrator

from app.utils.security import (
    verify_password,
    create_access_token,
)


def login_user(db: Session, login_data):

    try:
        # STEP 1: GET USER
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account inactive."
            )

        # STEP 2: VERIFY PASSWORD
        if not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # ==================================================
        # DOCTOR LOGIN
        # ==================================================
        doctor = db.query(Doctor).filter(
            Doctor.user_id == user.user_id
        ).first()

        if doctor:
            token_data = {
                "sub": str(user.user_id),          # ALWAYS user_id
                "email": user.email,
                "role": "doctor",
                "doctor_id": doctor.doctor_id     # 🔥 IMPORTANT FIX
            }

            access_token = create_access_token(token_data)

            return {
                "status_code": 200,
                "detail": "Login successful",
                "data": {
                    "access_token": access_token,
                    "role": "doctor"
                }
            }

        # ==================================================
        # ADMIN LOGIN
        # ==================================================
        administrator = db.query(Administrator).filter(
            Administrator.user_id == user.user_id
        ).first()

        if administrator:
            token_data = {
                "sub": str(user.user_id),            # ALWAYS user_id
                "email": user.email,
                "role": "administrator",
                "admin_id": administrator.admin_id   # optional
            }

            access_token = create_access_token(token_data)

            return {
                "status_code": 200,
                "detail": "Login successful",
                "data": {
                    "access_token": access_token,
                    "role": "administrator"
                }
            }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No linked role found."
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )