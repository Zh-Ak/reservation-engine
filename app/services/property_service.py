import datetime
import uuid

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.properties import Property
from app.models.users import User
from app.repositories import booking_repository, property_repository
from app.schemas.property import PropertyCreate, PropertyUpdate


async def create_property(session: AsyncSession, owner: User, data: PropertyCreate) -> Property:
    prop = Property(
        owner_id=owner.id,
        name=data.name.strip(),
        description=data.description,
        country=data.country.strip(),
        city=data.city.strip(),
        address=data.address.strip(),
    )
    prop = await property_repository.create(session, prop)
    await session.commit()
    return prop


async def list_my_properties(
    session: AsyncSession, owner: User, limit: int, offset: int
) -> list[Property]:
    return await property_repository.list_by_owner(session, owner.id, limit, offset)


async def get_property(session: AsyncSession, property_id: uuid.UUID) -> Property:
    prop = await property_repository.get_active(session, property_id)
    if prop is None:
        raise NotFoundError("Property not found")
    return prop


async def get_owned_property(session: AsyncSession, property_id: uuid.UUID, owner: User) -> Property:
    prop = await property_repository.get_active(session, property_id)
    # Someone else's property looks exactly like a missing one: 404, not 403.
    if prop is None or prop.owner_id != owner.id:
        raise NotFoundError("Property not found")
    return prop


async def update_property(
    session: AsyncSession, property_id: uuid.UUID, owner: User, data: PropertyUpdate
) -> Property:
    prop = await get_owned_property(session, property_id, owner)

    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(prop, field, value.strip() if isinstance(value, str) else value)

    await session.commit()
    return prop


async def delete_property(session: AsyncSession, property_id: uuid.UUID, owner: User) -> None:
    prop = await get_owned_property(session, property_id, owner)

    today = datetime.date.today()
    if await booking_repository.has_upcoming_bookings(session, today, property_id=prop.id):
        raise ConflictError("Property has upcoming bookings and cannot be deleted")

    prop.deleted_at = func.now()
    await session.commit()