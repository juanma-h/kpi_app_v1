from pydantic import BaseModel, EmailStr


class UserMe(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
