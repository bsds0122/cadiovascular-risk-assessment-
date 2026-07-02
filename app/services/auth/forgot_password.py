import os
import secrets

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# ==========================================================
# DATABASE MODELS
# ==========================================================
from app.models.user import User




def forgot_password(db: Session, email: str):
    
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return {
                "status_code": 200,
                "detail": "Reset link sent successfully, please check"
            }

        return {
            "status_code": 200,
            "detail": "Reset link sent successfully, please check"
        }

    except Exception as e:
        return {
            "status_code": 500,
            "detail": str(e)
        }