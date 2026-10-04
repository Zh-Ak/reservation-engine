from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.exceptions import LoginFailedError
from app.schemas.user import TokenResponse, UserLogin
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/login", response_model=TokenResponse)
async def login_user(data: UserLogin, session: SessionDep):
    try:
        access_token = await user_service.login(session, data)
    except LoginFailedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=access_token)