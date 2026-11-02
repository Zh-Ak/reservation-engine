import uuid

from fastapi import APIRouter, status

from app.dependencies.auth import ClientDep
from app.dependencies.db import SessionDep
from app.routes.pagination import Limit, Offset
from app.schemas.booking import BookingCreate, BookingResponse
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(data: BookingCreate, user: ClientDep, session: SessionDep):
    return await booking_service.create_booking(session, user, data)


@router.get("/mine", response_model=list[BookingResponse])
async def list_my_bookings(user: ClientDep, session: SessionDep, limit: Limit = 20, offset: Offset = 0):
    return await booking_service.list_my_bookings(session, user, limit, offset)


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: uuid.UUID, user: ClientDep, session: SessionDep):
    return await booking_service.get_my_booking(session, user, booking_id)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(booking_id: uuid.UUID, user: ClientDep, session: SessionDep):
    return await booking_service.cancel_booking(session, user, booking_id)