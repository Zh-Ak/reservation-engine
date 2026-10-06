from fastapi import APIRouter

from app.db.session import get_db_session
from app.exceptions import LoginFailedError
from app.schemas.user import TokenResponse, UserLogin
from app.services import user_service
from app.dependencies.db import SessionDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login_user(data: UserLogin, session: SessionDep):
    access_token = await user_service.login(session, data)
    return TokenResponse(access_token=access_token)