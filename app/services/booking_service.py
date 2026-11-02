import datetime
import uuid

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import BookingNotCancellableError, BusinessRuleError, NotFoundError, RoomNotAvailableError
from app.models.booking import Booking, BookingStatus
from app.models.users import User
from app.repositories import booking_repository, room_repository
from app.schemas.booking import BookingCreate
from app.services import property_service

OVERLAP_CONSTRAINT = "no_overlapping_confirmed_bookings"


def _violated_constraint(error: IntegrityError) -> str | None:
    """Name of the database constraint that rejected the write, if the driver reports it."""
    original = getattr(error.orig, "__cause__", None)  # the asyncpg exception
    return getattr(original, "constraint_name", None)


async def create_booking(session: AsyncSession, user: User, data: BookingCreate) -> Booking:
    # 1. Business rules that need the current date or the database.
    today = datetime.date.today()
    if data.start_date < today:
        raise BusinessRuleError("start_date cannot be in the past")
    nights = (data.end_date - data.start_date).days
    if nights > settings.max_booking_nights:
        raise BusinessRuleError(f"A stay can be at most {settings.max_booking_nights} nights")

    room_type = await room_repository.get_active_room_type(session, data.room_type_id)
    if room_type is None:
        raise NotFoundError("Room type not found")
    await property_service.get_property(session, room_type.property_id)  # property must be active

    if data.guest_count > room_type.capacity:
        raise BusinessRuleError(f"This room type fits at most {room_type.capacity} guests")

    total_price = room_type.price * nights  # price snapshot, frozen into the booking

    # 2. Try the free rooms one by one. The exclusion constraint is the real guard:
    #    if another request takes a room between our SELECT and our INSERT,
    #    Postgres rejects our INSERT and we move on to the next room.
    candidate_ids = await room_repository.find_free_instance_ids(
        session, room_type.id, data.start_date, data.end_date
    )

    for room_instance_id in candidate_ids:
        booking = Booking(
            user_id=user.id,
            room_instance_id=room_instance_id,
            start_date=data.start_date,
            end_date=data.end_date,
            guest_count=data.guest_count,
            total_price=total_price,
            status=BookingStatus.CONFIRMED,
        )
        try:
            async with session.begin_nested():  # SAVEPOINT
                session.add(booking)
                await session.flush()  # the INSERT runs here; constraints are checked here
        except IntegrityError as error:
            if _violated_constraint(error) == OVERLAP_CONSTRAINT:
                continue  # someone just took this room: try the next one
            raise

        await session.commit()
        await session.refresh(booking)
        return booking

    raise RoomNotAvailableError()


async def get_my_booking(session: AsyncSession, user: User, booking_id: uuid.UUID) -> Booking:
    booking = await booking_repository.get_by_id(session, booking_id)
    if booking is None or booking.user_id != user.id:
        raise NotFoundError("Booking not found")
    return booking


async def list_my_bookings(session: AsyncSession, user: User, limit: int, offset: int) -> list[Booking]:
    return await booking_repository.list_by_user(session, user.id, limit, offset)


async def list_property_bookings(
    session: AsyncSession, property_id: uuid.UUID, owner: User, limit: int, offset: int
) -> list[Booking]:
    prop = await property_service.get_owned_property(session, property_id, owner)
    return await booking_repository.list_by_property(session, prop.id, limit, offset)


async def cancel_booking(session: AsyncSession, user: User, booking_id: uuid.UUID) -> Booking:
    # FOR UPDATE: lock the row so two cancel requests cannot both pass the checks below.
    booking = await booking_repository.get_by_id(session, booking_id, for_update=True)
    if booking is None or booking.user_id != user.id:
        raise NotFoundError("Booking not found")
    if booking.status != BookingStatus.CONFIRMED:
        raise BookingNotCancellableError("Booking is already cancelled")
    if booking.start_date <= datetime.date.today():
        raise BookingNotCancellableError("Bookings can only be cancelled before the stay starts")

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = func.now()
    await session.commit()
    await session.refresh(booking)  # load cancelled_at, which the database filled in
    return booking