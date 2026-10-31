import datetime
import uuid

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.models.room_instance import RoomInstance
from app.models.room_type import RoomType


async def get_by_id(
    session: AsyncSession, booking_id: uuid.UUID, for_update: bool = False
) -> Booking | None:
    query = select(Booking).where(Booking.id == booking_id)
    if for_update:
        query = query.with_for_update()
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_by_idempotency_key(
    session: AsyncSession, user_id: uuid.UUID, idempotency_key: str
) -> Booking | None:
    query = select(Booking).where(
        Booking.user_id == user_id, Booking.idempotency_key == idempotency_key
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def list_by_user(
    session: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
) -> list[Booking]:
    query = (
        select(Booking)
        .where(Booking.user_id == user_id)
        .order_by(Booking.start_date.desc(), Booking.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def list_by_property(
    session: AsyncSession, property_id: uuid.UUID, limit: int, offset: int
) -> list[Booking]:
    query = (
        select(Booking)
        .join(RoomInstance, RoomInstance.id == Booking.room_instance_id)
        .join(RoomType, RoomType.id == RoomInstance.room_type_id)
        .where(RoomType.property_id == property_id)
        .order_by(Booking.start_date.desc(), Booking.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def has_upcoming_bookings(
    session: AsyncSession,
    today: datetime.date,
    *,
    property_id: uuid.UUID | None = None,
    room_type_id: uuid.UUID | None = None,
    room_instance_id: uuid.UUID | None = None,
) -> bool:
    """True if a confirmed booking that has not ended yet hangs off this property / room type / room."""
    query = (
        select(Booking.id)
        .join(RoomInstance, RoomInstance.id == Booking.room_instance_id)
        .join(RoomType, RoomType.id == RoomInstance.room_type_id)
        .where(Booking.status == BookingStatus.CONFIRMED, Booking.end_date > today)
    )
    if property_id is not None:
        query = query.where(RoomType.property_id == property_id)
    if room_type_id is not None:
        query = query.where(RoomType.id == room_type_id)
    if room_instance_id is not None:
        query = query.where(RoomInstance.id == room_instance_id)

    result = await session.execute(select(exists(query)))
    return bool(result.scalar())