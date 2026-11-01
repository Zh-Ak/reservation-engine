import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import BusinessRuleError
from app.repositories import search_repository
from app.schemas.search import AvailableRoomType


async def search_availability(
    session: AsyncSession,
    city: str,
    check_in: datetime.date,
    check_out: datetime.date,
    guests: int,
    limit: int,
    offset: int,
) -> list[AvailableRoomType]:
    if check_out <= check_in:
        raise BusinessRuleError("check_out must be after check_in")
    if check_in < datetime.date.today():
        raise BusinessRuleError("check_in cannot be in the past")
    nights = (check_out - check_in).days
    if nights > settings.max_booking_nights:
        raise BusinessRuleError(f"A stay can be at most {settings.max_booking_nights} nights")

    rows = await search_repository.search_available_room_types(
        session, city, check_in, check_out, guests, limit, offset
    )
    return [
        AvailableRoomType(**row, nights=nights, total_price=row["price_per_night"] * nights)
        for row in rows
    ]