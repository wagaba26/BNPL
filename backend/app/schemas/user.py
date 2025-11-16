from pydantic import BaseModel
from app.models.user import UserRole


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    role: UserRole

    class Config:
        from_attributes = True


class UserMe(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole

    class Config:
        from_attributes = True

