import uuid

from fastapi import APIRouter, status

from app.dependencies.auth import ProviderDep
from app.dependencies.db import SessionDep
from app.schemas.room import RoomInstanceCreate, RoomInstanceResponse, RoomTypeResponse, RoomTypeUpdate
from app.services import room_service

router = APIRouter(tags=["rooms"])


@router.patch("/room-types/{room_type_id}", response_model=RoomTypeResponse)
async def update_room_type(
    room_type_id: uuid.UUID, data: RoomTypeUpdate, owner: ProviderDep, session: SessionDep
):
    return await room_service.update_room_type(session, room_type_id, owner, data)


@router.delete("/room-types/{room_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_type(room_type_id: uuid.UUID, owner: ProviderDep, session: SessionDep):
    await room_service.delete_room_type(session, room_type_id, owner)


@router.post(
    "/room-types/{room_type_id}/rooms",
    response_model=RoomInstanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_room_instance(
    room_type_id: uuid.UUID, data: RoomInstanceCreate, owner: ProviderDep, session: SessionDep
):
    return await room_service.create_room_instance(session, room_type_id, owner, data)


@router.get("/room-types/{room_type_id}/rooms", response_model=list[RoomInstanceResponse])
async def list_room_instances(room_type_id: uuid.UUID, owner: ProviderDep, session: SessionDep):
    return await room_service.list_room_instances(session, room_type_id, owner)


@router.delete("/rooms/{room_instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_instance(room_instance_id: uuid.UUID, owner: ProviderDep, session: SessionDep):
    await room_service.delete_room_instance(session, room_instance_id, owner)