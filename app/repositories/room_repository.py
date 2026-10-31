import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.models.room_instance import RoomInstance
from app.models.room_type import RoomType


async def create_room_type(session: AsyncSession, room_type: RoomType) -> RoomType:
    session.add(room_type)
    await session.flush()
    await session.refresh(room_type)
    return room_type


async def get_active_room_type(session: AsyncSession, room_type_id: uuid.UUID) -> RoomType | None:
    query = select(RoomType).where(RoomType.id == room_type_id, RoomType.deleted_at.is_(None))
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def list_room_types(session: AsyncSession, property_id: uuid.UUID) -> list[RoomType]:
    query = (
        select(RoomType)
        .where(RoomType.property_id == property_id, RoomType.deleted_at.is_(None))
        .order_by(RoomType.price, RoomType.id)
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_room_instance(session: AsyncSession, room: RoomInstance) -> RoomInstance:
    session.add(room)
    await session.flush()
    await session.refresh(room)
    return room


async def get_active_room_instance(
    session: AsyncSession, room_instance_id: uuid.UUID
) -> RoomInstance | None:
    query = select(RoomInstance).where(
        RoomInstance.id == room_instance_id, RoomInstance.deleted_at.is_(None)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def list_room_instances(session: AsyncSession, room_type_id: uuid.UUID) -> list[RoomInstance]:
    query = (
        select(RoomInstance)
        .where(RoomInstance.room_type_id == room_type_id, RoomInstance.deleted_at.is_(None))
        .order_by(RoomInstance.label, RoomInstance.id)
    )
    result = await session.execute(query)
    return list(result.scalars().all())


def overlapping_booking_exists(check_in: datetime.date, check_out: datetime.date):
    """EXISTS(a confirmed booking on this room that overlaps [check_in, check_out))."""
    return (
        select(Booking.id)
        .where(
            Booking.room_instance_id == RoomInstance.id,
            Booking.status == BookingStatus.CONFIRMED,
            Booking.start_date < check_out,
            Booking.end_date > check_in,
        )
        .exists()
    )


async def find_free_instance_ids(
    session: AsyncSession,
    room_type_id: uuid.UUID,
    check_in: datetime.date,
    check_out: datetime.date,
) -> list[uuid.UUID]:
    query = (
        select(RoomInstance.id)
        .where(
            RoomInstance.room_type_id == room_type_id,
            RoomInstance.deleted_at.is_(None),
            ~overlapping_booking_exists(check_in, check_out),
        )
        .order_by(RoomInstance.label, RoomInstance.id)
    )
    result = await session.execute(query)
    return list(result.scalars().all())