from pydantic import BaseModel, EmailStr
from typing import Optional


class AdministratorProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    experience_years: Optional[int] = None
    hospital: Optional[str] = None
    profile_image: Optional[str] = None