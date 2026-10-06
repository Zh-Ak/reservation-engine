import uuid
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies.db import SessionDep
from app.exceptions import AuthenticationError
from app.models.users import User
from app.repositories import user_repository
from app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: SessionDep,
) -> User:
    if credentials is None:
        raise AuthenticationError()

    try:
        user_id = uuid.UUID(decode_access_token(credentials.credentials))
    except (jwt.InvalidTokenError, ValueError):
        raise AuthenticationError()

    user = await user_repository.get_by_id(session, user_id)
    if user is None:
        raise AuthenticationError()

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]