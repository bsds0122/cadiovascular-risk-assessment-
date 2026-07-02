from pydantic import BaseModel, EmailStr


class ContactCreate(BaseModel):
    email: EmailStr
    subject: str
    message: str