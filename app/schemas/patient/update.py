from pydantic import BaseModel
from typing import Optional
from datetime import date

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    next_of_kin_number: Optional[str] = None
    date_of_diagnosis: Optional[date] = None
    diabetes_type: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    traditional_authority: Optional[str] = None
    village: Optional[str] = None
    profile_image: Optional[str] = None
