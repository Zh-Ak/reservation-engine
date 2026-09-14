from pydantic import BaseModel, EmailStr
import enum
import datetime
import uuid
from app.models.users import UserRole

class RegistrationRole(str, enum.Enum):
    CLIENT = "client"
    PROVIDER = "provider"

class UserRequest(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    role: RegistrationRole

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    created_at: datetime.datetime
    role: UserRole
