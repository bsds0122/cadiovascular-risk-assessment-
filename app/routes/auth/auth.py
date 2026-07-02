from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

# ==========================================================
# DATABASE AND AUTHENTICATION DEPENDENCIES
# ==========================================================
from app.core.database import get_db
from app.dependencies.auth import get_current_user

# ==========================================================
# REQUEST SCHEMAS
# ==========================================================
from app.schemas.auth.login import (
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

# ==========================================================
# STANDARD API RESPONSE SCHEMA
# ==========================================================
from app.schemas.response import APIResponse

# ==========================================================
# AUTHENTICATION SERVICES
# ==========================================================
from app.services.auth.login import login_user
from app.services.auth.logout import logout_doctor
from app.services.auth.forgot_password import (
    forgot_password,
)

from app.schemas.auth.change_password import ChangePasswordRequest
from app.services.auth.change_password import change_password




# ==========================================================
# AUTHENTICATION AND ACCOUNT ACCESS MANAGEMENT ROUTES
# ==========================================================
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# ==========================================================
# AUTHENTICATE USER AND GENERATE ACCESS SESSION
# ==========================================================
@router.post(
    "/login",
    response_model=APIResponse,
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return access credentials.
    """

    # ------------------------------------------------------
    # Validate credentials and generate authentication data
    # ------------------------------------------------------
    results = login_user(
        db=db,
        login_data=login_data,
    )

    # ------------------------------------------------------
    # Return standardized login response
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        status="success",
        details=results["detail"],
        data=results.get("data"),
    )


# ==========================================================
# LOGOUT CURRENTLY AUTHENTICATED USER
# ==========================================================
@router.post(
    "/logout",
    response_model=APIResponse,
)
def logout(
    current_user=Depends(get_current_user),
):
    """
    Logout the authenticated user and invalidate the session.
    """

    # ------------------------------------------------------
    # Execute logout operation
    # ------------------------------------------------------
    results = logout_doctor(
        current_user=current_user,
    )

    # ------------------------------------------------------
    # Return logout confirmation response
    # ------------------------------------------------------
    return APIResponse(
        status_code=results["status_code"],
        status="success",
        details=results["detail"],
        data=results.get("data"),
    )


# ==========================================================
# REQUEST PASSWORD RESET LINK
# ==========================================================
@router.post(
    "/forgot-password",
    response_model=APIResponse,
)
async def forgot_password_endpoint(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a password reset token and send reset instructions
    to the user's registered email address.
    """

    # ------------------------------------------------------
    # Process forgot password request
    # ------------------------------------------------------
    result =  forgot_password(
        db=db,
        email=payload.email,
    )

    # ------------------------------------------------------
    # Return password reset request response
    # ------------------------------------------------------
    return APIResponse(
        status_code=result["status_code"],
        details=result["detail"],
    )


@router.post(
    "/change-password",
    response_model=APIResponse,
)
def change_password_endpoint(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
):
    result = change_password(
        db=db,
        default_password=payload.default_password,
        new_password=payload.new_password,
    )

    return APIResponse(
        status_code=result["status_code"],
        status="success",
        details=result["detail"],
        data=result.get("data"),
    )













