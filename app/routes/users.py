from fastapi import APIRouter, HTTPException, status

from app.db.session import get_db_session
from app.schemas.user import UserResponse, UserRequest, UserLogin
from app.services import user_service
from app.exceptions import EmailAlreadyExistsError
from app.dependencies.db import SessionDep


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(data: UserRequest, session: SessionDep):
    return await user_service.register(session, data)