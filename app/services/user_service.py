from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.concurrency import run_in_threadpool

from app.schemas.user import UserRequest
from app.models.users import User, UserRole
from app.repositories import user_repository
from app.security import hash_password

from app.exceptions import EmailAlreadyExistsError


async def register(session: AsyncSession, data: UserRequest) -> User: 
    email = data.email.strip().lower()

    if await user_repository.get_by_email(session, email) is not None:
        raise EmailAlreadyExistsError(email)
        
    password_hash = await run_in_threadpool(hash_password, data.password)

    user = User(
        name=data.name,
        surname=data.surname,
        email=email,
        role=UserRole(data.role.value),
        password_hash=password_hash,
    )

    try:
        user = await user_repository.create_user(session, user)
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        if await user_repository.get_by_email(session, email) is not None:
            raise EmailAlreadyExistsError(email) from e
        raise


    return user




    
        