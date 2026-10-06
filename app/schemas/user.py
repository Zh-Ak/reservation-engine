from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import enum
import datetime
import uuid
from app.models.users import UserRole

class RegistrationRole(str, enum.Enum):
    CLIENT = "client"
    PROVIDER = "provider"

class UserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    role: RegistrationRole

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("password must be at most 72 bytes")
        return value

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    created_at: datetime.datetime
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    passwods: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
