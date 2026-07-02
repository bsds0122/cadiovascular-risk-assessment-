from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class DoctorRegister(BaseModel):
    first_name: str
    last_name: str
    sex: str
    phone: str
    specialization: str
    hospital: str
    email: EmailStr
    experience_years: int = Field(ge=0, le=80)
    license_number: str
    profile_image: Optional[str] = None

  
class DoctorUpdate(BaseModel):
    # Doctor profile (all fields optional)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image: Optional[str] = None
    sex: Optional[str] = Field(
        default=None,
        description="Male or Female"
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=20
    )
    specialization: Optional[str] = None
    email: Optional[EmailStr] = None
    experience_years: Optional[int] = Field(
        default=None,
        ge=0,
        le=80
    )
    license_number: Optional[str] = None