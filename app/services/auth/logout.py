from fastapi import HTTPException, status

from app.services.auth.blacklist import add_token_to_blacklist


# ==========================================================
# DOCTOR LOGOUT (TOKEN BLACKLISTING)
# ==========================================================
def logout_doctor(current_user):
    """
    Logout the authenticated user by invalidating
    their current access token using a blacklist system.
    """

    try:
        # --------------------------------------------------
        # STEP 1: Extract token from authenticated user context
        # --------------------------------------------------
        token = current_user.get("token")

        # --------------------------------------------------
        # STEP 2: Validate token presence
        # --------------------------------------------------
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token.",
            )

        # --------------------------------------------------
        # STEP 3: Add token to blacklist (invalidate session)
        # --------------------------------------------------
        add_token_to_blacklist(token)

        # --------------------------------------------------
        # STEP 4: Return success response
        # --------------------------------------------------
        return {
            "status_code": status.HTTP_200_OK,
            "detail": "Logged out successfully.",
        }

    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to logout. Please try again.",
        )