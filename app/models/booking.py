import datetime
import decimal
import enum
import uuid

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Numeric, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BookingStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("end_date > start_date", name="ck_bookings_dates_order"),
        CheckConstraint("guest_count > 0", name="ck_bookings_guest_count_positive"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_bookings_user_idempotency_key"),
        ExcludeConstraint(
            ("room_instance_id", "="),
            (text("daterange(start_date, end_date)"), "&&"),
            using="gist",
            where=text("status = 'confirmed'"),
            name="no_overlapping_confirmed_bookings",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    room_instance_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("room_instances.id"))
    start_date: Mapped[datetime.date] = mapped_column(Date)
    end_date: Mapped[datetime.date] = mapped_column(Date)
    guest_count: Mapped[int] = mapped_column()
    total_price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[BookingStatus] = mapped_column(
        Enum(
            BookingStatus,
            name="bookingstatus",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        )
    )
    idempotency_key: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    cancelled_at: Mapped[datetime.datetime | None] = mapped_column(nullable=True)