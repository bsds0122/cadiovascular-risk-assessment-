from pydantic import BaseModel, EmailStr
from typing import Optional


class DoctorProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    hospital: Optional[str] = None
    license_number: Optional[str] = None
    profile_image: Optional[str] = None