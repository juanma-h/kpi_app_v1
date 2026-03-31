from pydantic import BaseModel, EmailStr

from app.domain.enums import UserRole


class UserMe(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
