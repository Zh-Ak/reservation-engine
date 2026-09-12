from app.db.base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, func, Enum, Date

import uuid
import datetime
import enum

class BookingStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    room_instance_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("room_instances.id"))
    start_date: Mapped[datetime.date] = mapped_column(Date)
    end_date: Mapped[datetime.date] = mapped_column(Date)
    guest_count: Mapped[int] = mapped_column()
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())