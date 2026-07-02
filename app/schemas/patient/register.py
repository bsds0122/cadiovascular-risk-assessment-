from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class PatientRegister(BaseModel):
    # ==========================================================
    # PERSONAL DETAILS
    # ==========================================================
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    sex: str = Field(..., max_length=10)

    # ==========================================================
    # CONTACT DETAILS
    # ==========================================================
    phone_number: str = Field(..., max_length=20)
    next_of_kin_number: str = Field(..., max_length=20)

    # ==========================================================
    # MEDICAL DETAILS
    # ==========================================================
    date_of_diagnosis: date
    diabetes_type: str = Field(..., max_length=50)

    # ==========================================================
    # LOCATION DETAILS
    # ==========================================================
    region: str = Field(..., max_length=100)
    district: str = Field(..., max_length=100)
    traditional_authority: str = Field(..., max_length=100)
    village: str = Field(..., max_length=100)

    # ==========================================================
    # PROFILE IMAGE
    # ==========================================================
    profile_image: Optional[str] = None