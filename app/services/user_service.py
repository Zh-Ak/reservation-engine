from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.concurrency import run_in_threadpool

from app.schemas.user import UserRequest, UserLogin
from app.models.users import User, UserRole
from app.repositories import user_repository
from app.security import hash_password, DUMMY_HASH, create_access_token, verify_password

from app.exceptions import EmailAlreadyExistsError, LoginFailedError


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

async def login(session: AsyncSession, data: UserLogin) -> str:
    email = data.email.strip().lower()

    user = await user_repository.get_by_email(session, email)

    hash_to_check = user.password_hash if user is not None else DUMMY_HASH
    password_ok = await run_in_threadpool(verify_password, data.password, hash_to_check)

    if user is None or not password_ok:
        raise LoginFailedError()

    return create_access_token(str(user.id))



    
        