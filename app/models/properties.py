from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, ForeignKey

import uuid
import datetime

from app.db.base import Base


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(nullable=True)