import uuid
import enum
import datetime

from sqlalchemy import Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class UserRole(str, enum.Enum):
    CLIENT = "client"
    PROVIDER = "provider"
    MODERATOR = "moderator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    surname: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())