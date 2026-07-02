from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field


class AdminRegister(BaseModel):

    # administrator profile
    first_name: str
    last_name: str
    sex: str = Field(description="Male or Female")
    email: EmailStr
    phone: str = Field(min_length=10, max_length=20)
    specialization: str
    experience_years: int = Field(ge=0, le=80)
    hospital: str
    profile_image: Optional[str] = None

   
  