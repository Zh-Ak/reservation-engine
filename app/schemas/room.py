import datetime
import decimal
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoomTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=5000)
    price: decimal.Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    capacity: int = Field(gt=0, le=20)


class RoomTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=5000)
    price: decimal.Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    capacity: int | None = Field(default=None, gt=0, le=20)

    @field_validator("name", "price", "capacity")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("this field cannot be null")
        return value


class RoomTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    property_id: uuid.UUID
    name: str
    description: str | None
    price: decimal.Decimal
    capacity: int
    created_at: datetime.datetime


class RoomInstanceCreate(BaseModel):
    label: str | None = Field(default=None, max_length=50)


class RoomInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    room_type_id: uuid.UUID
    label: str | None
    created_at: datetime.datetime