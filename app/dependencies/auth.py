from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.utils.security import SECRET_KEY, ALGORITHM
from app.services.auth.blacklist import is_token_blacklisted

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    # ❌ Check blacklist
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in again."
        )

    try:
        # 🔓 Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user = db.query(User).filter(User.email == payload.get("email")).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account inactive or not found."
            )

        # ✅ RETURN CLEAN STRUCTURE
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "doctor_id": payload.get("doctor_id")  # IMPORTANT
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please login again."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token."
        )