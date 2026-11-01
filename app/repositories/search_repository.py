import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.properties import Property
from app.models.room_instance import RoomInstance
from app.models.room_type import RoomType
from app.repositories.room_repository import overlapping_booking_exists


async def search_available_room_types(
    session: AsyncSession,
    city: str,
    check_in: datetime.date,
    check_out: datetime.date,
    guests: int,
    limit: int,
    offset: int,
):
    available_rooms = func.count(RoomInstance.id).label("available_rooms")
    query = (
        select(
            RoomType.id.label("room_type_id"),
            RoomType.name.label("room_type_name"),
            RoomType.capacity,
            RoomType.price.label("price_per_night"),
            Property.id.label("property_id"),
            Property.name.label("property_name"),
            Property.city,
            available_rooms,
        )
        .join(Property, Property.id == RoomType.property_id)
        .join(RoomInstance, RoomInstance.room_type_id == RoomType.id)
        .where(
            func.lower(Property.city) == city.strip().lower(),
            Property.deleted_at.is_(None),
            RoomType.deleted_at.is_(None),
            RoomInstance.deleted_at.is_(None),
            RoomType.capacity >= guests,
            ~overlapping_booking_exists(check_in, check_out),
        )
        .group_by(RoomType.id, Property.id)
        .order_by(RoomType.price, RoomType.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return result.mappings().all()