from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.user import UserResponse, UserRequest, UserLogin
from app.services import user_service
from app.exceptions import EmailAlreadyExistsError


router = APIRouter(prefix="/users", tags=["users"])

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data:UserRequest, session: SessionDep):
    try:
        return await user_service.register(session, data)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists"
        )