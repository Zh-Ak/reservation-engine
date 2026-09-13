from app.db.base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func, ForeignKey, Enum

import uuid
import datetime
import enum

class NotificationEvent(str, enum.Enum):
    BOOKING_CREATED = "booking_created"
    BOOKING_CANCELLED = "booking_cancelled"

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    booking_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("bookings.id"))
    event: Mapped[NotificationEvent] = mapped_column(Enum(NotificationEvent, values_callable=lambda x: [e.value for e in x]))
    delivered: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())