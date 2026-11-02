import uuid

from fastapi import APIRouter, status

from app.dependencies.auth import ProviderDep
from app.dependencies.db import SessionDep
from app.routes.pagination import Limit, Offset
from app.schemas.property import PropertyCreate, PropertyResponse, PropertyUpdate
from app.schemas.room import RoomTypeCreate, RoomTypeResponse
from app.services import property_service, room_service
from app.schemas.booking import BookingResponse
from app.services import booking_service, property_service, room_service

router = APIRouter(prefix="/properties", tags=["properties"])


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(data: PropertyCreate, owner: ProviderDep, session: SessionDep):
    return await property_service.create_property(session, owner, data)


@router.get("/mine", response_model=list[PropertyResponse])
async def list_my_properties(owner: ProviderDep, session: SessionDep, limit: Limit = 20, offset: Offset = 0):
    return await property_service.list_my_properties(session, owner, limit, offset)


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: uuid.UUID, session: SessionDep):
    return await property_service.get_property(session, property_id)


@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: uuid.UUID, data: PropertyUpdate, owner: ProviderDep, session: SessionDep
):
    return await property_service.update_property(session, property_id, owner, data)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(property_id: uuid.UUID, owner: ProviderDep, session: SessionDep):
    await property_service.delete_property(session, property_id, owner)


@router.post(
    "/{property_id}/room-types", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED
)
async def create_room_type(
    property_id: uuid.UUID, data: RoomTypeCreate, owner: ProviderDep, session: SessionDep
):
    return await room_service.create_room_type(session, property_id, owner, data)


@router.get("/{property_id}/room-types", response_model=list[RoomTypeResponse])
async def list_room_types(property_id: uuid.UUID, session: SessionDep):
    return await room_service.list_room_types(session, property_id)


@router.get("/{property_id}/bookings", response_model=list[BookingResponse])
async def list_property_bookings(
    property_id: uuid.UUID, owner: ProviderDep, session: SessionDep, limit: Limit = 20, offset: Offset = 0
):
    return await booking_service.list_property_bookings(session, property_id, owner, limit, offset)