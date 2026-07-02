from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    default_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)