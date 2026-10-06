from fastapi import APIRouter, status

from app.schemas.user import UserResponse, UserRequest
from app.services import user_service
from app.dependencies.db import SessionDep
from app.dependencies.auth import CurrentUserDep


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: UserRequest, session: SessionDep):
    return await user_service.register(session, data)


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: CurrentUserDep):
    return current_user