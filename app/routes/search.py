import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies.db import SessionDep
from app.routes.pagination import Limit, Offset
from app.schemas.search import AvailableRoomType
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/availability", response_model=list[AvailableRoomType])
async def search_availability(
    session: SessionDep,
    city: Annotated[str, Query(min_length=1, max_length=100)],
    check_in: datetime.date,
    check_out: datetime.date,
    guests: Annotated[int, Query(ge=1, le=20)] = 1,
    limit: Limit = 20,
    offset: Offset = 0,
):
    return await search_service.search_availability(
        session, city, check_in, check_out, guests, limit, offset
    )