from pydantic import BaseModel

class DoctorStatusUpdate(BaseModel):
    is_active: bool
