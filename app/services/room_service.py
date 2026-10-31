import datetime
import uuid

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.room_instance import RoomInstance
from app.models.room_type import RoomType
from app.models.users import User
from app.repositories import booking_repository, room_repository
from app.schemas.room import RoomInstanceCreate, RoomTypeCreate, RoomTypeUpdate
from app.services import property_service


async def _get_owned_room_type(session: AsyncSession, room_type_id: uuid.UUID, owner: User) -> RoomType:
    room_type = await room_repository.get_active_room_type(session, room_type_id)
    if room_type is None:
        raise NotFoundError("Room type not found")
    # Raises NotFoundError if the property is deleted or belongs to someone else.
    await property_service.get_owned_property(session, room_type.property_id, owner)
    return room_type


# ---- room types ----

async def create_room_type(
    session: AsyncSession, property_id: uuid.UUID, owner: User, data: RoomTypeCreate
) -> RoomType:
    prop = await property_service.get_owned_property(session, property_id, owner)
    room_type = RoomType(
        property_id=prop.id,
        name=data.name.strip(),
        description=data.description,
        price=data.price,
        capacity=data.capacity,
    )
    room_type = await room_repository.create_room_type(session, room_type)
    await session.commit()
    return room_type


async def list_room_types(session: AsyncSession, property_id: uuid.UUID) -> list[RoomType]:
    prop = await property_service.get_property(session, property_id)
    return await room_repository.list_room_types(session, prop.id)


async def update_room_type(
    session: AsyncSession, room_type_id: uuid.UUID, owner: User, data: RoomTypeUpdate
) -> RoomType:
    room_type = await _get_owned_room_type(session, room_type_id, owner)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(room_type, field, value)
    await session.commit()
    return room_type


async def delete_room_type(session: AsyncSession, room_type_id: uuid.UUID, owner: User) -> None:
    room_type = await _get_owned_room_type(session, room_type_id, owner)
    today = datetime.date.today()
    if await booking_repository.has_upcoming_bookings(session, today, room_type_id=room_type.id):
        raise ConflictError("Room type has upcoming bookings and cannot be deleted")
    room_type.deleted_at = func.now()
    await session.commit()


# ---- room instances (the physical rooms) ----

async def create_room_instance(
    session: AsyncSession, room_type_id: uuid.UUID, owner: User, data: RoomInstanceCreate
) -> RoomInstance:
    room_type = await _get_owned_room_type(session, room_type_id, owner)
    room = RoomInstance(room_type_id=room_type.id, label=data.label)
    room = await room_repository.create_room_instance(session, room)
    await session.commit()
    return room


async def list_room_instances(
    session: AsyncSession, room_type_id: uuid.UUID, owner: User
) -> list[RoomInstance]:
    room_type = await _get_owned_room_type(session, room_type_id, owner)
    return await room_repository.list_room_instances(session, room_type.id)


async def delete_room_instance(session: AsyncSession, room_instance_id: uuid.UUID, owner: User) -> None:
    room = await room_repository.get_active_room_instance(session, room_instance_id)
    if room is None:
        raise NotFoundError("Room not found")
    await _get_owned_room_type(session, room.room_type_id, owner)

    today = datetime.date.today()
    if await booking_repository.has_upcoming_bookings(session, today, room_instance_id=room.id):
        raise ConflictError("Room has upcoming bookings and cannot be deleted")
    room.deleted_at = func.now()
    await session.commit()