from pydantic import BaseModel, EmailStr, field_validator
from app.models.user import UserRole
import re


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    username: str | None = None  # Optional username
    password: str
    phone: str | None = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None:
            # Username validation: alphanumeric, underscore, hyphen, 3-30 chars
            if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', v):
                raise ValueError('Username must be 3-30 characters and contain only letters, numbers, underscores, or hyphens')
        return v


class UserLogin(BaseModel):
    email_or_username: str  # Can be either email or username
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserMe"


class UserMe(BaseModel):
    id: int
    name: str
    username: str | None = None
    email: str
    role: UserRole

    class Config:
        from_attributes = True


Token.model_rebuild()

