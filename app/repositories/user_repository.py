from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user


async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user