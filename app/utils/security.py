import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# =========================
# PASSWORD HASHING
# =========================
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# =========================
# JWT CREATION (FIXED)
# =========================
def create_access_token(data: dict) -> str:
    """
    Create a clean JWT access token with standard claims.
    """

    now = datetime.now(timezone.utc)

    payload = {
        # 🔥 REQUIRED IDENTITY CLAIMS
        "sub": str(data.get("sub")),   # user_id (always string)
        "role": data.get("role"),
        "email": data.get("email"),

        # 🔥 OPTIONAL DOMAIN CLAIMS
        "doctor_id": data.get("doctor_id"),
        "admin_id": data.get("admin_id"),

        # 🔥 SYSTEM CLAIMS
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "token_type": "access",
    }

    # Remove None values (IMPORTANT CLEANUP)
    payload = {k: v for k, v in payload.items() if v is not None}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)