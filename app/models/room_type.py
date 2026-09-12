from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, func, Numeric

import uuid
import datetime
import decimal

from app.db.base import Base


class RoomType(Base):
    __tablename__ = "room_types"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id"), index=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column(nullable=True)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2))
    capacity: Mapped[int] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(nullable=True)