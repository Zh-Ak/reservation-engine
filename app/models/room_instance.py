from app.db.base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, func

import uuid
import datetime


class RoomInstance(Base):
    __tablename__ = "room_instances"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    room_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("room_types.id"), index=True)
    label: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(nullable=True)