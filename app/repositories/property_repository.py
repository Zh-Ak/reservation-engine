import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.properties import Property


async def create(session: AsyncSession, prop: Property) -> Property:
    session.add(prop)
    await session.flush()
    await session.refresh(prop)
    return prop


async def get_active(session: AsyncSession, property_id: uuid.UUID) -> Property | None:
    query = select(Property).where(Property.id == property_id, Property.deleted_at.is_(None))
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def list_by_owner(
    session: AsyncSession, owner_id: uuid.UUID, limit: int, offset: int
) -> list[Property]:
    query = (
        select(Property)
        .where(Property.owner_id == owner_id, Property.deleted_at.is_(None))
        .order_by(Property.created_at.desc(), Property.id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    return list(result.scalars().all())